# Tech Context

## バックエンド（api/）
- Python 3.11+ / FastAPI 0.116 / Uvicorn(開発) / Gunicorn(本番)
- SQLAlchemy 2.0 + Alembic / psycopg2 / PostgreSQL 16
- PyJWT + passlib(bcrypt) / Pillow + OpenCV + ImageHash
- httpx / pandas / rapidfuzz / python-multipart

## フロントエンド（vue/ ★主力）
- Vue 3.4+ / Vite 5 / Vuetify 3.6+ / TypeScript 5.6 / Pinia 2.1+
- ファイルベースルーティング: unplugin-vue-router
- API: Axios（現メイン）+ openapi-fetch（型安全、移行先）
- pnpm / Sass(modern-compiler)

## 環境変数（主要）
| 変数 | 説明 |
|------|------|
| SQLALCHEMY_DATABASE_URL | DB接続文字列 |
| SECRET_KEY | JWT署名キー |
| DATA_ROOT | データディレクトリ（/opt/data） |
| CONVERT_THREAD | Worker並列度 |
| VITE_APP_API_HOST | APIホスト（フロントエンド） |

## 開発コマンド
```bash
# API
python3 main.py           # 開発サーバー
python3 worker.py          # Worker
alembic revision --autogenerate -m "説明"
alembic upgrade head

# フロントエンド
cd vue/ && pnpm dev        # 開発サーバー(:3000)
pnpm build                 # ビルド

# 型生成
npx openapi-typescript http://localhost:8000/openapi.json -o ./src/api.d.ts
```

## ポート
| ポート | サービス |
|--------|----------|
| 80 | Nginx（本番） |
| 3000 | Vite開発サーバー |
| 8000 | FastAPI |
| 5432 | PostgreSQL |
