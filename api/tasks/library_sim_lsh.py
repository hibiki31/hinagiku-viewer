"""
LSH（Locality-Sensitive Hashing）を使用した高速重複検出
8万冊規模でも実用的な速度で処理可能
"""
import datetime
import uuid
import sys
from collections import defaultdict
from typing import List, Tuple, Set, Dict
from multiprocessing import Pool

import imagehash
from PIL import Image
from sqlalchemy import or_
from sqlalchemy.orm import Session

from books.models import BookModel, DuplicationModel, DuplicateSettingsModel
from mixins.log import setup_logger
from settings import CONVERT_THREAD, DATA_ROOT

logger = setup_logger(__name__)


class LSHIndex:
    """LSH（Locality-Sensitive Hashing）インデックス"""
    
    def __init__(self, num_bands: int = 16, band_size: int = 16):
        """
        Args:
            num_bands: バンド数（デフォルト16）
            band_size: 各バンドのビット数（デフォルト16）
        """
        self.num_bands = num_bands
        self.band_size = band_size
        self.buckets: List[Dict[int, List[str]]] = [defaultdict(list) for _ in range(num_bands)]
        logger.info(f"LSHインデックス初期化: {num_bands}バンド × {band_size}ビット")
    
    def _hash_to_bands(self, hash_str: str) -> List[int]:
        """ハッシュ文字列をバンドに分割"""
        hash_int = int(hash_str, 16)
        bands = []
        for band_idx in range(self.num_bands):
            shift = band_idx * self.band_size
            mask = (1 << self.band_size) - 1
            band_value = (hash_int >> shift) & mask
            bands.append(band_value)
        return bands
    
    def add(self, uuid: str, hash_str: str):
        """書籍をインデックスに追加"""
        if not hash_str:
            return
        bands = self._hash_to_bands(hash_str)
        for band_idx, band_value in enumerate(bands):
            self.buckets[band_idx][band_value].append(uuid)
    
    def get_candidates(self, uuid: str, hash_str: str) -> Set[str]:
        """候補となる類似書籍のUUIDセットを取得"""
        if not hash_str:
            return set()
        
        candidates = set()
        bands = self._hash_to_bands(hash_str)
        
        for band_idx, band_value in enumerate(bands):
            # 同じバンド値を持つ書籍を候補に追加
            bucket = self.buckets[band_idx].get(band_value, [])
            for candidate_uuid in bucket:
                if candidate_uuid != uuid:
                    candidates.add(candidate_uuid)
        
        return candidates


def calculate_hamming_distance(hash1: str, hash2: str) -> int:
    """2つのハッシュ間のハミング距離を計算"""
    if not hash1 or not hash2:
        return 999
    h1 = int(hash1, 16)
    h2 = int(hash2, 16)
    return bin(h1 ^ h2).count('1')


def get_hash_from_thumbnail(book_uuid: str) -> Tuple[str, str, str]:
    """
    サムネイルから3種類のハッシュを計算
    Returns: (ahash, phash, dhash)
    """
    try:
        image = Image.open(f'{DATA_ROOT}/book_thum/{book_uuid}.jpg')
        ahash = str(imagehash.average_hash(image, hash_size=16))
        phash = str(imagehash.phash(image, hash_size=16))
        dhash = str(imagehash.dhash(image, hash_size=16))
        return (ahash, phash, dhash)
    except Exception as e:
        logger.error(f"ハッシュ計算エラー {book_uuid}: {e}")
        return (None, None, None)


def process_hash_batch(args: Tuple[List[str], int, int]) -> List[Dict]:
    """マルチプロセス用: バッチでハッシュを計算"""
    book_uuids, start, end = args
    logger.info(f"ハッシュ計算開始: {start}-{end}")
    
    results = []
    for book_uuid in book_uuids[start:end]:
        ahash, phash, dhash = get_hash_from_thumbnail(book_uuid[0])
        if ahash:
            results.append({
                "uuid": book_uuid[0],
                "ahash": ahash,
                "phash": phash,
                "dhash": dhash
            })
            if len(results) % 100 == 0:
                logger.debug(f"進捗: {len(results)}件完了")
    
    logger.info(f"ハッシュ計算完了: {start}-{end} ({len(results)}件)")
    return results


def compute_multi_hash(db: Session, mode: str = "missing"):
    """
    マルチハッシュ（ahash, phash, dhash）を計算
    
    Args:
        mode: "missing" = 未計算のみ, "all" = 全件再計算
    """
    # 対象書籍を取得
    if mode == "all":
        books = db.query(BookModel.uuid).all()
        logger.info(f"全件ハッシュ計算: {len(books)}冊")
    else:
        books = db.query(BookModel.uuid).filter(
            or_(
                BookModel.ahash == None,
                BookModel.phash == None,
                BookModel.dhash == None
            )
        ).all()
        logger.info(f"未計算ハッシュを計算: {len(books)}冊")
    
    if len(books) == 0:
        logger.info("計算対象なし")
        return
    
    # 少数の場合はシングルスレッド
    if len(books) <= 16:
        for book in books:
            ahash, phash, dhash = get_hash_from_thumbnail(book.uuid)
            if ahash:
                db_book = db.query(BookModel).filter(BookModel.uuid == book.uuid).one()
                db_book.ahash = ahash
                db_book.phash = phash
                db_book.dhash = dhash
                logger.info(f"{book.uuid}: ahash={ahash}, phash={phash}, dhash={dhash}")
        db.commit()
        return
    
    # 大量の場合はマルチプロセス
    size = len(books)
    batch_size = max(100, size // CONVERT_THREAD)
    
    logger.info(f"{CONVERT_THREAD}スレッドで{size}冊のハッシュを計算（バッチサイズ: {batch_size}）")
    
    # バッチ作成
    batches = []
    for i in range(0, size, batch_size):
        batches.append((books, i, min(i + batch_size, size)))
    
    # マルチプロセス実行
    with Pool(CONVERT_THREAD) as pool:
        results = pool.map(process_hash_batch, batches)
    
    # 結果を統合
    all_results = [item for batch in results for item in batch]
    logger.info(f"{len(all_results)}件のハッシュを取得、DBに書き込み中...")
    
    # DB更新
    for result in all_results:
        book = db.query(BookModel).filter(BookModel.uuid == result["uuid"]).one()
        book.ahash = result["ahash"]
        book.phash = result["phash"]
        book.dhash = result["dhash"]
    
    db.commit()
    logger.info("DBへの書き込み完了")


def find_duplicates_lsh(db: Session, settings: DuplicateSettingsModel):
    """
    LSHアルゴリズムで重複を検出
    
    処理フロー:
    1. 全書籍のハッシュをLSHインデックスに登録
    2. 各書籍について候補を抽出
    3. 候補のみ詳細比較（ハミング距離計算）
    4. マルチハッシュ戦略で判定
    """
    logger.info("=== LSH重複検出開始 ===")
    
    # 設定値
    ahash_threshold = settings.ahash_threshold
    phash_threshold = settings.phash_threshold
    dhash_threshold = settings.dhash_threshold
    lsh_bands = settings.lsh_bands
    lsh_band_size = settings.lsh_band_size
    
    logger.info(f"閾値: ahash={ahash_threshold}, phash={phash_threshold}, dhash={dhash_threshold}")
    logger.info(f"LSH設定: {lsh_bands}バンド × {lsh_band_size}ビット")
    
    # 全書籍のハッシュを取得
    books = db.query(
        BookModel.uuid,
        BookModel.ahash,
        BookModel.phash,
        BookModel.dhash
    ).filter(
        BookModel.ahash != None
    ).all()
    
    book_count = len(books)
    logger.info(f"{book_count}冊の書籍を処理")
    
    if book_count == 0:
        logger.warning("ハッシュが計算された書籍がありません")
        return
    
    # LSHインデックス構築（ahashベース）
    logger.info("LSHインデックス構築中...")
    lsh_ahash = LSHIndex(num_bands=lsh_bands, band_size=lsh_band_size)
    
    # ハッシュマップ作成（UUID → ハッシュ）
    hash_map = {}
    for book in books:
        uuid = book.uuid
        hash_map[uuid] = {
            'ahash': book.ahash,
            'phash': book.phash,
            'dhash': book.dhash
        }
        lsh_ahash.add(uuid, book.ahash)
    
    logger.info("LSHインデックス構築完了")
    
    # 候補ペア抽出
    logger.info("候補ペア抽出中...")
    candidate_pairs = set()
    
    for idx, book in enumerate(books):
        if idx % 1000 == 0:
            logger.info(f"進捗: {idx}/{book_count}冊処理")
        
        uuid = book.uuid
        # LSHで候補抽出
        candidates = lsh_ahash.get_candidates(uuid, book.ahash)
        
        # ペアを登録（UUID順でソートして重複防止）
        for candidate_uuid in candidates:
            pair = tuple(sorted([uuid, candidate_uuid]))
            candidate_pairs.add(pair)
    
    logger.info(f"候補ペア数: {len(candidate_pairs)}ペア（全組み合わせ: {book_count * (book_count - 1) // 2}）")
    logger.info(f"削減率: {100 * (1 - len(candidate_pairs) / max(1, book_count * (book_count - 1) // 2)):.2f}%")
    
    # 詳細比較
    logger.info("詳細比較中...")
    duplicates = []
    
    for idx, (uuid1, uuid2) in enumerate(candidate_pairs):
        if idx % 10000 == 0 and idx > 0:
            logger.info(f"詳細比較進捗: {idx}/{len(candidate_pairs)}ペア")
        
        h1 = hash_map[uuid1]
        h2 = hash_map[uuid2]
        
        # マルチハッシュ戦略: いずれか1つが閾値以下なら重複候補
        ahash_score = calculate_hamming_distance(h1['ahash'], h2['ahash'])
        phash_score = calculate_hamming_distance(h1['phash'], h2['phash'])
        dhash_score = calculate_hamming_distance(h1['dhash'], h2['dhash'])
        
        # 判定ロジック: ahashが最も厳しく、phash/dhashで補完
        is_duplicate = False
        min_score = ahash_score
        
        if ahash_score < ahash_threshold:
            # ahashで明確に一致
            is_duplicate = True
            min_score = ahash_score
        elif phash_score < phash_threshold and dhash_score < dhash_threshold:
            # phashとdhash両方で類似
            is_duplicate = True
            min_score = min(phash_score, dhash_score)
        elif phash_score < phash_threshold - 2:
            # phashが非常に類似
            is_duplicate = True
            min_score = phash_score
        
        if is_duplicate:
            duplicates.append((uuid1, uuid2, min_score))
            logger.debug(f"重複検出: {uuid1} <-> {uuid2} (scores: a={ahash_score}, p={phash_score}, d={dhash_score})")
    
    logger.info(f"重複ペア数: {len(duplicates)}ペア")
    
    # Union-Find で重複グループを構築
    logger.info("重複グループ構築中...")
    parent = {}
    
    def find(x):
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    for uuid1, uuid2, _ in duplicates:
        union(uuid1, uuid2)
    
    # グループごとに集約
    groups = defaultdict(list)
    for uuid1, uuid2, score in duplicates:
        root = find(uuid1)
        groups[root].append((uuid1, uuid2, score))
    
    logger.info(f"重複グループ数: {len(groups)}グループ")
    
    # DBに保存
    logger.info("DBに保存中...")
    
    # 既存の重複データを削除
    db.query(DuplicationModel).delete()
    db.commit()
    
    # 新しい重複データを保存
    for group_root, pairs in groups.items():
        group_id = str(uuid.uuid4())
        
        # グループ内の全UUIDを集める
        uuids_in_group = set()
        for uuid1, uuid2, _ in pairs:
            uuids_in_group.add(uuid1)
            uuids_in_group.add(uuid2)
        
        # 全ペアを保存
        for uuid1, uuid2, score in pairs:
            db.merge(DuplicationModel(
                duplication_id=group_id,
                book_uuid_1=uuid1,
                book_uuid_2=uuid2,
                score=score
            ))
    
    db.commit()
    logger.info("=== LSH重複検出完了 ===")


def main(db: Session, mode: str = "all"):
    """
    メイン処理
    
    Args:
        mode: "all" = 全件処理, "incremental" = 増分処理
    """
    logger.info(f"重複検出開始 (mode={mode})")
    
    # 設定を取得
    settings = db.query(DuplicateSettingsModel).filter(DuplicateSettingsModel.id == 1).first()
    if not settings:
        logger.warning("重複検出設定が見つかりません。デフォルト値を使用します")
        settings = DuplicateSettingsModel(
            id=1,
            ahash_threshold=10,
            phash_threshold=12,
            dhash_threshold=15,
            lsh_bands=16,
            lsh_band_size=16,
            updated_at=datetime.datetime.now()
        )
    
    # ステップ1: ハッシュ計算
    if mode == "all":
        compute_multi_hash(db, mode="all")
    else:
        compute_multi_hash(db, mode="missing")
    
    # ステップ2: 重複検出
    find_duplicates_lsh(db, settings)
    
    logger.info("全処理完了")


if __name__ == "__main__":
    from mixins.database import SessionLocal
    db = SessionLocal()
    main(db, mode="all")
