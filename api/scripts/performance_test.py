"""
APIパフォーマンステストスクリプト

使用方法:
    # 通常実行（APIから書籍一覧を取得して計測）
    python3 scripts/performance_test.py

    # リプレイデータを保存して実行
    python3 scripts/performance_test.py --save-replay

    # 保存済みリプレイで実行（同じ本・キーワードで比較計測）
    python3 scripts/performance_test.py --use-replay

    # クライアント数・URLを指定
    python3 scripts/performance_test.py --clients 10 --base-url http://localhost:8000

    # 結果をJSONファイルに出力
    python3 scripts/performance_test.py --output results.json

設定ファイル: tests/env.json
リプレイファイル: scripts/perf_replay.json
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx

# ============================= 定数 =============================

# デフォルト設定ファイルパス
ENV_FILE = Path(__file__).parent.parent / "tests" / "env.json"

# リプレイデータ保存先
REPLAY_FILE = Path(__file__).parent / "perf_replay.json"

# デフォルトクライアント数
DEFAULT_CLIENTS = 10

# 各クライアントが担当する書籍数
BOOKS_PER_CLIENT = 3

# 書籍検索に使う最大書籍数（クライアント数 × 担当冊数分確保）
# DEFAULT_CLIENTS * BOOKS_PER_CLIENT = 30
MAX_BOOKS_IN_REPLAY = 30

# 画像取得時の高さ（ピクセル）
IMAGE_HEIGHT = 1080

# HTTPタイムアウト（秒）
HTTP_TIMEOUT = 60.0

# 全文検索キーワード候補（リプレイデータがない場合のデフォルト）
DEFAULT_KEYWORDS = [
    "vol",
    "comic",
    "01",
    "the",
    "2024",
]


# ============================= データクラス =============================


@dataclass
class RequestResult:
    """1回のリクエスト結果"""

    scenario: str
    method: str
    url: str
    status_code: int
    duration_ms: float
    error: str | None = None

    @property
    def success(self) -> bool:
        """成功判定（2xx系）"""
        return 200 <= self.status_code < 300


@dataclass
class ReplayData:
    """リプレイデータ（書籍一覧・キーワード一覧を保存して再利用）"""

    base_url: str
    books: list[dict] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    library_ids: list[int] = field(default_factory=list)
    saved_at: str = ""

    def save(self, path: Path) -> None:
        """リプレイデータをJSONファイルに保存する"""
        data = {
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "base_url": self.base_url,
            "books": self.books,
            "keywords": self.keywords,
            "library_ids": self.library_ids,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  リプレイデータを保存しました: {path}")

    @classmethod
    def load(cls, path: Path) -> ReplayData:
        """JSONファイルからリプレイデータを読み込む"""
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            base_url=data.get("base_url", ""),
            books=data.get("books", []),
            keywords=data.get("keywords", DEFAULT_KEYWORDS),
            library_ids=data.get("library_ids", [1]),
            saved_at=data.get("saved_at", ""),
        )


# ============================= 計測ヘルパー =============================


def _measure(
    client: httpx.Client,
    scenario: str,
    method: str,
    url: str,
    **kwargs,
) -> RequestResult:
    """HTTPリクエストを計測して RequestResult を返す"""
    start = time.perf_counter()
    try:
        resp = client.request(method, url, **kwargs)
        duration_ms = (time.perf_counter() - start) * 1000
        return RequestResult(
            scenario=scenario,
            method=method,
            url=url,
            status_code=resp.status_code,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        return RequestResult(
            scenario=scenario,
            method=method,
            url=url,
            status_code=0,
            duration_ms=duration_ms,
            error=str(exc),
        )


# ============================= シナリオ =============================


def scenario_library_list(
    client: httpx.Client,
    base_url: str,
    headers: dict,
) -> list[RequestResult]:
    """S1-a: ライブラリ一覧取得"""
    result = _measure(
        client,
        scenario="S1-a ライブラリ一覧",
        method="GET",
        url=f"{base_url}/api/libraries",
        headers=headers,
    )
    return [result]


def scenario_book_list(
    client: httpx.Client,
    base_url: str,
    headers: dict,
    library_ids: list[int],
) -> list[RequestResult]:
    """S1-b: 書籍一覧取得（ページネーションあり）"""
    results = []
    lib_id = random.choice(library_ids) if library_ids else 1

    # 1ページ目
    result = _measure(
        client,
        scenario="S1-b 書籍一覧(page1)",
        method="GET",
        url=f"{base_url}/api/books",
        headers=headers,
        params={"libraryId": lib_id, "limit": 50, "offset": 0, "sortKey": "addDate"},
    )
    results.append(result)

    # 2ページ目
    result = _measure(
        client,
        scenario="S1-b 書籍一覧(page2)",
        method="GET",
        url=f"{base_url}/api/books",
        headers=headers,
        params={"libraryId": lib_id, "limit": 50, "offset": 50, "sortKey": "addDate"},
    )
    results.append(result)

    return results


def scenario_title_search(
    client: httpx.Client,
    base_url: str,
    headers: dict,
    keywords: list[str],
    library_ids: list[int],
) -> list[RequestResult]:
    """S1-c: タイトル検索"""
    results = []
    lib_id = random.choice(library_ids) if library_ids else 1

    for keyword in keywords[:3]:  # 最大3キーワード
        result = _measure(
            client,
            scenario="S1-c タイトル検索",
            method="GET",
            url=f"{base_url}/api/books",
            headers=headers,
            params={
                "libraryId": lib_id,
                "titleLike": keyword,
                "limit": 20,
                "offset": 0,
            },
        )
        results.append(result)

    return results


def scenario_fulltext_search(
    client: httpx.Client,
    base_url: str,
    headers: dict,
    keywords: list[str],
    library_ids: list[int],
) -> list[RequestResult]:
    """S1-d: 全文検索（タイトル・著者・タグ横断）"""
    results = []
    lib_id = random.choice(library_ids) if library_ids else 1

    for keyword in keywords[:3]:  # 最大3キーワード
        result = _measure(
            client,
            scenario="S1-d 全文検索",
            method="GET",
            url=f"{base_url}/api/books",
            headers=headers,
            params={
                "libraryId": lib_id,
                "fullText": keyword,
                "limit": 20,
                "offset": 0,
            },
        )
        results.append(result)

    return results


def scenario_thumbnail(
    client: httpx.Client,
    base_url: str,
    client_books: list[dict],
) -> list[RequestResult]:
    """S2: サムネイル取得（クライアントに割り当てられた全書籍を対象）"""
    results = []
    for book in client_books:
        result = _measure(
            client,
            scenario="S2 サムネイル取得",
            method="GET",
            url=f"{base_url}/media/books/{book['uuid']}",
        )
        results.append(result)

    return results


def scenario_page_images(
    client: httpx.Client,
    base_url: str,
    client_books: list[dict],
) -> list[RequestResult]:
    """S3: ページ画像全ページ取得（本によって速度差が出る高負荷シナリオ）

    クライアントに割り当てられた全書籍の全ページを取得する。
    本のページ数や画像サイズにより処理時間が大きく異なる。
    """
    results = []
    for book in client_books:
        total_pages = book.get("page", 1)
        for page in range(1, total_pages + 1):
            result = _measure(
                client,
                scenario="S3 ページ画像取得",
                method="GET",
                url=f"{base_url}/media/books/{book['uuid']}/{page}",
                params={"height": IMAGE_HEIGHT},
            )
            results.append(result)

    return results


# ============================= クライアントワーカー =============================


def run_client(
    client_id: int,
    base_url: str,
    headers: dict,
    replay: ReplayData,
    client_books: list[dict],
) -> list[RequestResult]:
    """
    1クライアント分のシナリオをすべて実行する。

    Args:
        client_id: クライアントID（ログ用）
        base_url: APIのベースURL
        headers: 認証ヘッダー
        replay: リプレイデータ（書籍・キーワード）
        client_books: このクライアントに割り当てられた担当書籍（全ページ取得対象）

    Returns:
        このクライアントが実行したリクエスト結果一覧
    """
    all_results: list[RequestResult] = []

    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        # S1-a: ライブラリ一覧
        all_results.extend(scenario_library_list(client, base_url, headers))

        # S1-b: 書籍一覧取得
        all_results.extend(scenario_book_list(client, base_url, headers, replay.library_ids))

        # S1-c: タイトル検索
        if replay.keywords:
            all_results.extend(
                scenario_title_search(client, base_url, headers, replay.keywords, replay.library_ids)
            )

        # S1-d: 全文検索
        if replay.keywords:
            all_results.extend(
                scenario_fulltext_search(client, base_url, headers, replay.keywords, replay.library_ids)
            )

        # S2: 担当書籍のサムネイル取得
        if client_books:
            all_results.extend(scenario_thumbnail(client, base_url, client_books))

        # S3: 担当書籍の全ページ画像取得（高負荷・本によって処理速度が変わる）
        if client_books:
            all_results.extend(scenario_page_images(client, base_url, client_books))

    total_pages = sum(b.get("page", 0) for b in client_books)
    print(
        f"  クライアント {client_id:02d}: 完了 "
        f"({len(all_results)} リクエスト, 担当 {len(client_books)} 冊 / {total_pages} ページ)"
    )
    return all_results


# ============================= リポート =============================

# ANSI カラー
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _color_status(success_rate: float) -> str:
    if success_rate >= 99:
        return _GREEN
    if success_rate >= 90:
        return _YELLOW
    return _RED


def print_report(results: list[RequestResult], total_duration_s: float) -> None:
    """シナリオ別の統計レポートを表示する"""
    print()
    print(f"{_BOLD}{'=' * 70}{_RESET}")
    print(f"{_BOLD}  性能テスト結果{_RESET}")
    print(f"{'=' * 70}")

    # シナリオ別に集計
    scenarios: dict[str, list[RequestResult]] = {}
    for r in results:
        scenarios.setdefault(r.scenario, []).append(r)

    for scenario_name, reqs in sorted(scenarios.items()):
        total = len(reqs)
        successes = [r for r in reqs if r.success]
        failures = [r for r in reqs if not r.success]
        success_rate = len(successes) / total * 100 if total > 0 else 0

        durations = [r.duration_ms for r in reqs]
        avg = statistics.mean(durations) if durations else 0
        median = statistics.median(durations) if durations else 0
        p90 = _percentile(durations, 90)
        p95 = _percentile(durations, 95)
        p99 = _percentile(durations, 99)
        max_d = max(durations) if durations else 0

        color = _color_status(success_rate)
        print(f"\n{_CYAN}[{scenario_name}]{_RESET}")
        print(
            f"  リクエスト数: {total} "
            f"({color}成功: {len(successes)}{_RESET}, "
            f"{_RED}失敗: {len(failures)}{_RESET}) "
            f"成功率: {color}{success_rate:.1f}%{_RESET}"
        )
        print(
            f"  応答時間(ms): "
            f"avg={avg:7.1f} | "
            f"p50={median:7.1f} | "
            f"p90={p90:7.1f} | "
            f"p95={p95:7.1f} | "
            f"p99={p99:7.1f} | "
            f"max={max_d:7.1f}"
        )
        if failures:
            for r in failures[:3]:  # エラーは最大3件表示
                print(f"  {_RED}  エラー: [{r.status_code}] {r.url} - {r.error}{_RESET}")

    # 全体サマリー
    total_req = len(results)
    total_success = sum(1 for r in results if r.success)
    throughput = total_req / total_duration_s if total_duration_s > 0 else 0
    all_durations = [r.duration_ms for r in results]

    print()
    print(f"{'=' * 70}")
    print(f"{_BOLD}  全体サマリー{_RESET}")
    print(f"{'=' * 70}")
    print(f"  テスト時間: {total_duration_s:.1f}s")
    print(f"  総リクエスト数: {total_req} (成功: {total_success}, 失敗: {total_req - total_success})")
    print(f"  スループット: {throughput:.1f} req/s")
    if all_durations:
        print(
            f"  全体応答時間(ms): "
            f"avg={statistics.mean(all_durations):.1f} | "
            f"p90={_percentile(all_durations, 90):.1f} | "
            f"p99={_percentile(all_durations, 99):.1f}"
        )
    print(f"{'=' * 70}")


def _percentile(data: list[float], p: int) -> float:
    """パーセンタイルを計算する"""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = (len(sorted_data) - 1) * p / 100
    lower = int(idx)
    upper = lower + 1
    if upper >= len(sorted_data):
        return sorted_data[lower]
    frac = idx - lower
    return sorted_data[lower] * (1 - frac) + sorted_data[upper] * frac


def save_json_report(results: list[RequestResult], path: Path, total_duration_s: float) -> None:
    """結果をJSONファイルに保存する"""
    scenarios: dict[str, list[RequestResult]] = {}
    for r in results:
        scenarios.setdefault(r.scenario, []).append(r)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_duration_s": total_duration_s,
        "total_requests": len(results),
        "total_success": sum(1 for r in results if r.success),
        "scenarios": {},
    }

    for scenario_name, reqs in scenarios.items():
        durations = [r.duration_ms for r in reqs]
        report["scenarios"][scenario_name] = {
            "count": len(reqs),
            "success": sum(1 for r in reqs if r.success),
            "failure": sum(1 for r in reqs if not r.success),
            "avg_ms": statistics.mean(durations) if durations else 0,
            "median_ms": statistics.median(durations) if durations else 0,
            "p90_ms": _percentile(durations, 90),
            "p95_ms": _percentile(durations, 95),
            "p99_ms": _percentile(durations, 99),
            "max_ms": max(durations) if durations else 0,
        }

    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  結果をJSONに保存しました: {path}")


# ============================= 準備処理 =============================


def login(base_url: str, username: str, password: str) -> str:
    """ログインしてアクセストークンを取得する"""
    resp = httpx.post(
        f"{base_url}/api/auth",
        data={"username": username, "password": password},
        timeout=HTTP_TIMEOUT,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"ログイン失敗: {resp.status_code} {resp.text}")
    return resp.json()["access_token"]


def fetch_replay_data(base_url: str, headers: dict) -> ReplayData:
    """APIから書籍一覧・ライブラリ一覧を取得してリプレイデータを作成する"""
    # ライブラリ一覧取得
    resp = httpx.get(f"{base_url}/api/libraries", headers=headers, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    libraries = resp.json()
    print(f"  ライブラリ数: {len(libraries)} 件")

    # 一番本が多いライブラリを選択
    if libraries:
        best_library = max(libraries, key=lambda lib: lib.get("count", 0))
        library_ids = [best_library["id"]]
        print(
            f"  使用ライブラリ: ID={best_library['id']} "
            f"名前={best_library.get('name', '')} "
            f"({best_library.get('count', 0)} 冊)"
        )
    else:
        library_ids = [1]
        print("  ライブラリが見つかりません。デフォルトID=1を使用します。")

    # 書籍一覧取得（最も本が多いライブラリから）
    lib_id = library_ids[0]
    resp = httpx.get(
        f"{base_url}/api/books",
        headers=headers,
        params={"libraryId": lib_id, "limit": MAX_BOOKS_IN_REPLAY, "offset": 0, "sortKey": "addDate"},
        timeout=HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    book_data = resp.json()
    books_raw = book_data.get("rows", [])

    # リプレイ用に必要なフィールドのみ保存
    books = [
        {
            "uuid": b["uuid"],
            "title": b.get("title", ""),
            "page": b.get("page", 1),
            "library_id": b.get("libraryId", lib_id),
        }
        for b in books_raw
        if b.get("page", 0) > 0  # ページ数0の本はスキップ
    ]

    print(f"  書籍数: {len(books)} 件（最大 {MAX_BOOKS_IN_REPLAY} 件）")

    # キーワード候補: 書籍タイトルから抽出（先頭2文字）
    keywords = list({b["title"][:2] for b in books if b.get("title") and len(b["title"]) >= 2})
    keywords = keywords[:5]  # 最大5キーワード
    if not keywords:
        keywords = DEFAULT_KEYWORDS

    print(f"  検索キーワード: {keywords}")

    return ReplayData(
        base_url=base_url,
        books=books,
        keywords=keywords,
        library_ids=library_ids,
    )


# ============================= エントリーポイント =============================


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(
        description="APIパフォーマンステスト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="APIのベースURL（省略時はtests/env.jsonから読み込み）",
    )
    parser.add_argument(
        "--username",
        default=None,
        help="ログインユーザー名（省略時はtests/env.jsonから読み込み）",
    )
    parser.add_argument(
        "--password",
        default=None,
        help="ログインパスワード（省略時はtests/env.jsonから読み込み）",
    )
    parser.add_argument(
        "--clients",
        type=int,
        default=DEFAULT_CLIENTS,
        help=f"同時クライアント数（デフォルト: {DEFAULT_CLIENTS}）",
    )
    parser.add_argument(
        "--save-replay",
        action="store_true",
        help="APIから書籍一覧を取得してリプレイデータを保存する",
    )
    parser.add_argument(
        "--use-replay",
        action="store_true",
        help="保存済みリプレイデータを使用する（同じ本・キーワードで比較計測）",
    )
    parser.add_argument(
        "--replay-file",
        default=str(REPLAY_FILE),
        help=f"リプレイファイルパス（デフォルト: {REPLAY_FILE}）",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="結果をJSONファイルに出力するパス",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    replay_path = Path(args.replay_file)

    # --- 設定ファイル読み込み ---
    env: dict = {}
    if ENV_FILE.exists():
        env = json.loads(ENV_FILE.read_text(encoding="utf-8"))

    base_url: str = args.base_url or env.get("base_url", "http://localhost:8000")
    username: str = args.username or env.get("username", "test")
    password: str = args.password or env.get("password", "test")

    print(f"{_BOLD}===== APIパフォーマンステスト ====={_RESET}")
    print(f"  対象URL   : {base_url}")
    print(f"  ユーザー  : {username}")
    print(f"  クライアント数: {args.clients}")

    # --- 認証 ---
    print("\n[1/3] ログイン中...")
    try:
        token = login(base_url, username, password)
    except Exception as exc:
        print(f"{_RED}  ログイン失敗: {exc}{_RESET}")
        return
    print("  ログイン成功")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # --- リプレイデータ準備 ---
    print("\n[2/3] リプレイデータ準備中...")

    if args.use_replay and replay_path.exists():
        # 保存済みリプレイデータを読み込む
        replay = ReplayData.load(replay_path)
        print(f"  リプレイデータを読み込みました: {replay_path}")
        print(f"  保存日時: {replay.saved_at}")
        print(f"  書籍数: {len(replay.books)} 件 / キーワード: {replay.keywords}")
    else:
        if args.use_replay:
            print(f"  {_YELLOW}リプレイファイルが存在しないためAPIから取得します: {replay_path}{_RESET}")
        # APIから取得
        try:
            replay = fetch_replay_data(base_url, headers)
        except Exception as exc:
            print(f"{_RED}  データ取得失敗: {exc}{_RESET}")
            return

        # --save-replay が指定された場合は保存
        if args.save_replay:
            replay.save(replay_path)

    if not replay.books:
        print(f"{_RED}  書籍データが取得できませんでした。終了します。{_RESET}")
        return

    # --- 書籍をクライアントに割り当て ---
    # 書籍プールが不足する場合はラップアラウンドして割り当てる
    book_pool = replay.books
    total_needed = args.clients * BOOKS_PER_CLIENT
    if len(book_pool) < total_needed:
        # 書籍が足りない場合はサイクルして繰り返す
        repeated = (book_pool * ((total_needed // len(book_pool)) + 1))[:total_needed]
        print(
            f"  {_YELLOW}書籍数({len(book_pool)})が必要数({total_needed})より少ないため繰り返し割り当てます{_RESET}"
        )
    else:
        repeated = book_pool[:total_needed]

    client_book_assignments: list[list[dict]] = [
        repeated[i * BOOKS_PER_CLIENT : (i + 1) * BOOKS_PER_CLIENT]
        for i in range(args.clients)
    ]

    # 割り当て内容を表示（書籍名は表示しない）
    for i, books_assigned in enumerate(client_book_assignments):
        total_pages = sum(b.get("page", 0) for b in books_assigned)
        print(f"  クライアント {i + 1:02d}: {len(books_assigned)} 冊 (計 {total_pages} ページ)")

    # --- 並列実行 ---
    print(f"\n[3/3] {args.clients} クライアントで並列実行中...")
    all_results: list[RequestResult] = []
    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=args.clients) as executor:
        futures = {
            executor.submit(
                run_client, i + 1, base_url, headers, replay, client_book_assignments[i]
            ): i + 1
            for i in range(args.clients)
        }
        for future in as_completed(futures):
            client_id = futures[future]
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as exc:
                print(f"  {_RED}クライアント {client_id:02d}: 実行エラー - {exc}{_RESET}")

    total_duration = time.perf_counter() - start_time

    # --- レポート出力 ---
    print_report(all_results, total_duration)

    # --- JSON出力（オプション）---
    if args.output:
        save_json_report(all_results, Path(args.output), total_duration)


if __name__ == "__main__":
    main()
