# Tech Context - API Module

## コア技術
- **Python 3.11+** / **FastAPI 0.116** / Uvicorn(開発) / Gunicorn(本番)
- **SQLAlchemy 2.0** (Mapped型アノテーション) + **Alembic** + **psycopg2**
- **PyJWT** + **passlib**(bcrypt) — JWT認証
- **Pillow** + **OpenCV** + **ImageHash** — 画像処理・重複検出
- httpx, pandas, rapidfuzz, python-multipart

## 重要な設定値
- `API_VERSION = '3.0.0'`（settings.py ハードコード）
- `ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30`（30日）
- `SECRET_KEY = 'DEV_KEY'`（開発時固定、本番は環境変数）
- `CONVERT_THREAD = os.cpu_count()`（Worker並列度）
- 重複検出: hash_size=16(256bit), 閾値 score<10

## ファイルパス
```
/opt/data/
├── book_library/   # 永続保存
├── book_cache/     # サムネイルキャッシュ
├── book_send/      # インポート監視フォルダ
├── book_export/    # エクスポート先
├── book_fail/      # 失敗ファイル
└── app_data/       # ログ等
```

## 開発コマンド
```bash
python3 main.py                          # 開発サーバー(:8000)
python3 worker.py                        # Worker起動
alembic revision --autogenerate -m "説明"
alembic upgrade head
ruff check . --fix
```

## マイグレーション履歴
- 20211224: 初期
- 20230822: cached_status追加
- 20230929: ahash + duplication_table
- 20240105: is_favorite
- 20250830: テーブル名変更
- 20260210: マルチハッシュカラム + タイポ修正
