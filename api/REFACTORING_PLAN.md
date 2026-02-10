# リファクタリング計画書

**日付**: 2026/02/10  
**対象**: hinagiku-viewer APIモジュール  
**目的**: FastAPIベストプラクティスに準拠した命名規則への統一

---

## 概要

本ドキュメントは、hinagiku-viewer APIモジュールにおける関数名・変数名のリファクタリング計画を記載します。
リファクタリングは段階的に実施し、技術的負債を解消します。

---

## フェーズ1: 非破壊的変更 ✅ **完了**

### 目的
外部APIに影響を与えずに、内部の命名規則を改善する。

### 実施内容

#### 1.1 ファイル名の変更
| 変更前 | 変更後 | 理由 |
|--------|--------|------|
| `mixins/purser.py` | `mixins/parser.py` | purse（財布）ではなく、parse（解析）が正しい |

#### 1.2 クラス名の改善
| 変更前 | 変更後 | 箇所 |
|--------|--------|------|
| `PurseResult` | `ParseResult` | `mixins/parser.py` |
| `DebugTimer.rap()` | `DebugTimer.lap()` | `mixins/convertor.py`, `mixins/utility.py` |

#### 1.3 関数名の改善
| 変更前 | 変更後 | 箇所 | 理由 |
|--------|--------|------|------|
| `base_purser()` | `parse_filename()` | `mixins/parser.py` | 明確な動詞+名詞の構造 |
| `old_purser()` | `old_parser()` | `mixins/parser.py` | 一貫性のため |
| `make_thum()` | `make_thumbnail()` | `mixins/convertor.py` | 省略形を避ける |
| `is_copping()` | `is_copying()` | `mixins/convertor.py` | タイポ修正 |

#### 1.4 変数名の改善
| 変更前 | 変更後 | 箇所 |
|--------|--------|------|
| `file_name_purse` | `parsed_filename` | `tasks/library_import.py`, `tasks/library_fixmetadata.py` |

#### 1.5 影響を受けたファイル
- ✅ `mixins/parser.py` (新規作成)
- ✅ `mixins/convertor.py` (関数名修正)
- ✅ `books/router.py` (インポート更新)
- ✅ `tags/router.py` (インポート更新)
- ✅ `user_datas/router.py` (インポート更新)
- ✅ `tasks/library_import.py` (インポート・関数呼び出し更新)
- ✅ `tasks/library_fixmetadata.py` (インポート・関数呼び出し更新)
- ✅ `mixins/purser.py` (削除)

#### 1.6 ドキュメント追加
- 各関数にdocstringを追加
- 型ヒントの明確化
- パラメータと戻り値の説明

### 影響範囲
- **外部API**: 影響なし（エンドポイントURL、パラメータ名、レスポンス構造は不変）
- **既存クライアント**: 互換性あり
- **データベース**: 変更なし

### 検証方法
```bash
# OpenAPI JSON再生成
python3 main.py

# 開発サーバー起動
python3 main.py
```

---

## フェーズ2: Pydanticスキーマのエイリアス対応 ✅ **完了**

### 目的
Python内部ではsnake_caseを使用し、OpenAPI（フロントエンド）向けにはcamelCaseを自動変換する。
Pydanticの`alias_generator=to_camel`を活用することで、**非破壊的**かつ**自動的**にコードの一貫性を保つ。

### 実施内容

#### 2.1 BaseSchemaへのalias_generator設定

**mixins/schema.py:**
```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class BaseSchema(BaseModel):
    """全体共通の情報をセットするBaseSchema"""

    model_config = ConfigDict(
        alias_generator=to_camel,       # snake_case → camelCase 自動変換
        from_attributes=True,           # ORMモデルからの変換を有効化
        populate_by_name=True,          # snake_caseとcamelCaseの両方を受け入れる
    )
```

**使用例:**
```python
from mixins.schema import BaseSchema

class BookSchema(BaseSchema):
    # Python側: snake_case（自動的にcamelCaseに変換される）
    file_name: str              # → fileName
    is_favorite: bool = False   # → isFavorite
    series_id: int | None = None  # → seriesId
    
    # 特殊ケース: 変換ルールと異なる場合のみ個別にaliasを指定
    series_number: int = Field(default=None, alias="seriesNo")  # number → no
```

**FastAPIでの使用:**
```python
@router.get("/api/books", response_model=list[BookSchema])
async def list_books(
    file_name_like: str | None = Query(None, alias="fileNameLike"),
    author_like: str | None = Query(None, alias="authorLike"),
    # ...
):
    # Python内部ではsnake_caseを使用
    if file_name_like:
        query = query.filter(Book.file_name.like(f"%{file_name_like}%"))
```

**OpenAPI出力時:**
- FastAPIは自動的にエイリアスを使用してOpenAPIスキーマを生成
- レスポンスは`response_model_by_alias=True`（デフォルト）により自動的にcamelCaseに変換

#### 2.2 影響を受けるファイル

##### スキーマ定義の修正
- `books/schemas.py` - 全スキーマにエイリアス追加
- `authors/schemas.py` - 全スキーマにエイリアス追加
- `tags/schemas.py` - 全スキーマにエイリアス追加
- `users/schemas.py` - 全スキーマにエイリアス追加
- `user_datas/schemas.py` - 全スキーマにエイリアス追加

##### ルーター定義の修正
- `books/router.py` - クエリパラメータにエイリアス追加、内部処理をsnake_caseに統一
- `authors/router.py` - クエリパラメータにエイリアス追加
- `tags/router.py` - 必要に応じてエイリアス追加
- `users/router.py` - 必要に応じてエイリアス追加

##### モデル定義の確認
- `books/models.py` - カラム名の確認（既存のタイポは維持）
- `users/models.py` - カラム名の確認

#### 2.3 データベースカラム名のタイポ対応

**段階的アプローチ:**

**Phase 2a: Python側のみ正しい名前を使う**
```python
class BookSchema(BaseModel):
    # Python側は正しい名前
    cached: bool = Field(..., alias="chached")  # OpenAPIではタイポを維持
    is_shared: bool = Field(..., alias="isShered")  # OpenAPIではタイポを維持
    
    class Config:
        populate_by_name = True
```

**Phase 2b: 将来的にOpenAPI側も修正（破壊的変更）**
- フロントエンド修正後に`alias`を削除して正しい名前に統一

#### 2.4 具体的な変更例

**books/schemas.py:**
```python
from pydantic import BaseModel, Field
from datetime import datetime

class BookBase(BaseModel):
    file_name: str = Field(..., alias="fileName")
    author: str | None = Field(default=None)
    title: str | None = Field(default=None)
    series_id: int | None = Field(default=None, alias="seriesId")
    series_number: float | None = Field(default=None, alias="seriesNo")
    genre_id: int | None = Field(default=None, alias="genreId")
    library_id: int = Field(..., alias="libraryId")
    is_favorite: bool = Field(default=False, alias="isFavorite")
    
    # データベースのタイポをPython側では正しく扱う
    cached: bool = Field(default=False, alias="chached")
    is_shared: bool = Field(default=False, alias="isShered")
    
    class Config:
        populate_by_name = True
        from_attributes = True

class BookGet(BookBase):
    uuid: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
```

**books/router.py:**
```python
@router.get("/api/books", response_model=list[BookGet])
async def list_books(
    # クエリパラメータもエイリアスを使用
    file_name_like: str | None = Query(None, alias="fileNameLike"),
    author_like: str | None = Query(None, alias="authorLike"),
    title_like: str | None = Query(None, alias="titleLike"),
    full_text: str | None = Query(None, alias="fullText"),
    series_id: int | None = Query(None, alias="seriesId"),
    genre_id: int | None = Query(None, alias="genreId"),
    library_id: int | None = Query(None, alias="libraryId"),
    sort_key: str = Query("created_at", alias="sortKey"),
    sort_desc: bool = Query(True, alias="sortDesc"),
    db: Session = Depends(get_db),
):
    # Python内部では全てsnake_caseで統一
    query = db.query(Book)
    
    if file_name_like:
        query = query.filter(Book.file_name.like(f"%{file_name_like}%"))
    
    if author_like:
        query = query.filter(Book.author.like(f"%{author_like}%"))
    
    # ソート処理もsnake_caseで統一
    if sort_desc:
        query = query.order_by(desc(getattr(Book, sort_key)))
    else:
        query = query.order_by(asc(getattr(Book, sort_key)))
    
    return query.all()
```

#### 2.5 FastAPIのレスポンスモード設定

**main.py:**
```python
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    default_response_class=ORJSONResponse,
    # レスポンスモデルのエイリアスを有効化（デフォルトでTrue）
)

# 各エンドポイントでは明示的な設定は不要
# response_model_by_alias=True がデフォルト
```

### 影響範囲
- **外部API**: 🟢 **影響なし** - camelCaseは維持される
- **既存クライアント**: 🟢 **完全互換** - フロントエンド修正不要
- **データベース**: 🟢 **変更なし** - マイグレーション不要
- **Python内部**: 🟢 **一貫性向上** - snake_caseに統一

### メリット
- ✅ **非破壊的変更**: フロントエンドは一切修正不要
- ✅ **Pythonの規約準拠**: 内部コードがPEP 8に準拠
- ✅ **段階的移行**: 将来的にフロントエンド側も修正可能
- ✅ **型安全性**: Pydanticの型チェック機能を最大限活用
- ✅ **OpenAPI互換**: Swagger UIでもcamelCaseで表示

### リスク
- 🟡 **低**: エイリアス設定のミス（テストで検出可能）
- 🟡 **低**: 既存コードの読み替えが必要（レビューで対応）

### 検証方法
1. OpenAPI仕様書の確認（camelCaseが維持されているか）
   ```bash
   python3 main.py
   curl http://localhost:8000/openapi.json | jq '.components.schemas.BookGet'
   ```

2. Swagger UIでのテスト
   ```bash
   # ブラウザで http://localhost:8000/docs を開く
   ```

3. 既存のフロントエンドでの動作確認
   ```bash
   cd /workspace/vue
   pnpm dev
   # 書籍一覧、詳細、検索などが正常に動作するか確認
   ```

4. 型定義の再生成と確認
   ```bash
   cd /workspace/vue
   npx openapi-typescript http://localhost:8000/openapi.json -o ./src/api.d.ts
   # 生成されたファイルがcamelCaseのままか確認
   ```

---

## フェーズ3: データベースカラム名修正 ⚠️ **将来的な課題**

### 目的
データベースの実際のカラム名のタイポを修正する（オプション）。

### 背景
フェーズ2でPython側では正しい名前を使用できるようになったが、データベースの物理カラム名は依然として`chached`と`is_shered`のままである。
この段階は、将来的にデータベースを完全に整理したい場合のみ実施する。

### 実施予定の変更

#### 3.1 データベースカラム名
| テーブル | 変更前 | 変更後 | 理由 |
|----------|--------|--------|------|
| `books` | `chached` | `cached` | タイポ修正（cached=キャッシュ済み） |
| `books` | `is_shered` | `is_shared` | タイポ修正（shared=共有済み） |

#### 3.2 必要な作業

##### Alembicマイグレーション作成
```bash
cd /workspace/api
alembic revision --autogenerate -m "カラム名のタイポ修正: chached→cached, is_shered→is_shared"
alembic upgrade head
```

##### マイグレーションファイル例
```python
"""カラム名のタイポ修正

Revision ID: XXXXXXXXX
Revises: 7d7ba6b08aaa
Create Date: 2026-02-XX XX:XX:XX
"""

def upgrade():
    op.alter_column('books', 'chached', new_column_name='cached')
    op.alter_column('books', 'is_shered', new_column_name='is_shared')

def downgrade():
    op.alter_column('books', 'cached', new_column_name='chached')
    op.alter_column('books', 'is_shared', new_column_name='is_shered')
```

##### モデル定義の修正
```python
# books/models.py
class Book(Base):
    __tablename__ = "books"
    
    # カラム名を修正
    cached = Column(Boolean, default=False)  # 旧: chached
    is_shared = Column(Boolean, default=False)  # 旧: is_shered
```

##### スキーマ定義の修正
```python
# books/schemas.py
class BookBase(BaseModel):
    # エイリアスを削除または変更
    cached: bool = Field(default=False, alias="cached")  # camelCaseに変更する場合
    is_shared: bool = Field(default=False, alias="isShared")
```

#### 3.3 影響を受けるファイル
- `books/models.py` - モデル定義の修正
- `books/router.py` - クエリ・フィルタの修正
- `books/schemas.py` - エイリアスの更新
- `tasks/library_import.py` - カラム参照の修正
- その他、該当カラムを参照する全ファイル

### 影響範囲
- **外部API**: ⚠️ **条件付き破壊的変更** - エイリアスを変更する場合のみ
- **既存クライアント**: エイリアスを維持すれば互換性あり
- **データベース**: 🔴 **スキーマ変更**（マイグレーション必要）

### リスク
- 🔴 **高**: 本番環境のデータベーススキーマ変更
- 🟡 **中**: マイグレーション中のダウンタイム
- 🟢 **低**: エイリアスを維持すればフロントエンド修正不要

### 推奨事項
- この段階は**任意**とし、データベースの完全性が重要な場合のみ実施
- フェーズ2の実施後、数ヶ月の安定稼働を確認してから検討

---

## フェーズ4: 追加の命名規則統一 🟢 **推奨**

### 目的
残りの命名規則を統一する（エイリアス方式を使用）。

### 実施予定の変更

#### 4.1 スキーマプロパティ名の統一
| クラス | 変更前 | 変更後 | エイリアス |
|--------|--------|--------|-----------|
| `BookPut` | `series_no` | `series_number` | `seriesNo` |

```python
class BookPut(BaseModel):
    series_number: float | None = Field(default=None, alias="seriesNo")
```

#### 4.2 追加のエイリアス設定
全てのスキーマで残っているcamelCaseプロパティを確認し、必要に応じてエイリアスを追加。

### 影響範囲
- **外部API**: 🟢 **影響なし**
- **既存クライアント**: 🟢 **完全互換**
- **データベース**: 🟢 **変更なし**

---

## フェーズ5: エンドポイント関数名の改善 ✅ **完了**

### 目的
エンドポイント関数名をより意味的に明確にする（内部のみ、URL不変）。

### 実施予定の変更

#### 5.1 関数名の改善（books/router.py）
| 変更前 | 変更後 | 理由 |
|--------|--------|------|
| `get_api_library()` | `list_libraries()` | RESTful命名規則 |
| `get_api_books()` | `list_books()` | RESTful命名規則 |
| `change_book_data()` | `update_books()` | 一貫性のある動詞 |
| `delete_book_data()` | `delete_book()` | シンプル化 |

#### 5.2 関数名の改善（users/router.py）
| 変更前 | 変更後 |
|--------|--------|
| `read_api_users()` | `list_users()` |
| `read_api_users_me()` | `get_current_user_info()` |
| `post_api_users()` | `create_user()` |

#### 5.3 関数名の改善（authors/router.py）
| 変更前 | 変更後 |
|--------|--------|
| `get_api_library()` | `list_authors()` |
| `post_api_books_uuid_authors()` | `add_book_author()` |
| `delete_api_books_uuid_authors()` | `remove_book_author()` |
| `patch_api_authors()` | `update_author()` |

#### 5.4 関数名の改善（tags/router.py）
| 変更前 | 変更後 |
|--------|--------|
| `append_tag()` | `add_book_tag()` |
| `delete_tag()` | `remove_book_tag()` |
| `show_tag()` | `list_tags()` |

### 影響範囲
- **外部API**: 影響なし（URLとHTTPメソッドは不変）
- **既存クライアント**: 互換性あり
- **データベース**: 変更なし

---

## 実施推奨順序

### 推奨スケジュール

#### 🟢 即時実施可能（非破壊的変更）
1. ✅ **フェーズ1**: 非破壊的変更（完了）
2. ✅ **フェーズ2**: Pydanticスキーマのエイリアス対応（完了）
3. ✅ **フェーズ4**: 追加の命名規則統一（完了 - series_number対応済み）
4. ✅ **フェーズ5**: エンドポイント関数名の改善（完了 - 2026/02/10）

#### 🟡 将来的に検討
5. ⏳ **フェーズ3**: データベースカラム名修正（オプション、破壊的変更の可能性）

### フェーズ2の実施計画

**ステップ1: スキーマファイルの更新**
```bash
# 1. books/schemas.py にエイリアスを追加
# 2. authors/schemas.py にエイリアスを追加
# 3. tags/schemas.py にエイリアスを追加
# 4. users/schemas.py にエイリアスを追加
# 5. user_datas/schemas.py にエイリアスを追加
```

**ステップ2: ルーターファイルの更新**
```bash
# 1. books/router.py のクエリパラメータにエイリアス追加
# 2. authors/router.py のクエリパラメータにエイリアス追加
# 3. 内部処理を全てsnake_caseに統一
```

**ステップ3: 検証**
```bash
# 1. OpenAPI仕様書の生成と確認
python3 main.py
curl http://localhost:8000/openapi.json | jq '.components.schemas'

# 2. Swagger UIでの動作確認
# ブラウザで http://localhost:8000/docs

# 3. Vue 3フロントエンドでの動作確認
cd /workspace/vue
pnpm dev
```

**ステップ4: 型定義の再生成**
```bash
cd /workspace/vue
npx openapi-typescript http://localhost:8000/openapi.json -o ./src/api.d.ts
# camelCaseが維持されているか確認
```

---

## ロールバック計画

### フェーズ1のロールバック
```bash
# Gitで前のコミットに戻す
git revert HEAD
```

### フェーズ2のロールバック
```bash
# エイリアス追加はコード変更のみなので簡単にロールバック可能
git revert <commit-hash>

# データベース変更なし、マイグレーション不要
```

### フェーズ3のロールバック（実施する場合）
```bash
# マイグレーションのダウングレード
alembic downgrade -1

# コードのロールバック
git revert <commit-hash>
```

---

## 参考資料

### Pydanticエイリアス
- [Pydantic Field Aliases](https://docs.pydantic.dev/latest/concepts/fields/#field-aliases)
- [Pydantic Model Config](https://docs.pydantic.dev/latest/concepts/config/)

### FastAPI命名規則
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)

### RESTful API設計
- CRUD操作の動詞: `create`, `list`, `get`, `update`, `delete`
- エンドポイント関数名: `<verb>_<resource>` 形式

### データベースマイグレーション
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)

---

## まとめ

### 完了した作業
- ✅ フェーズ1: 非破壊的変更（2026/02/10完了）
  - 内部の命名規則を改善
  - 外部APIに影響なし
  - 技術的負債の一部解消

- ✅ フェーズ2: Pydanticスキーマのエイリアス対応（2026/02/10完了）
  - Python側: snake_case
  - OpenAPI側: camelCase（自動変換）
  - フロントエンド修正不要

- ✅ フェーズ4: 追加の命名規則統一（2026/02/10完了）
  - series_numberで対応済み

- ✅ フェーズ5: エンドポイント関数名の改善（2026/02/10完了）
  - 14箇所の関数名をRESTful命名規則に準拠
  - books/router.py: 4箇所変更
  - users/router.py: 3箇所変更
  - authors/router.py: 4箇所変更
  - tags/router.py: 3箇所変更
  - 外部APIに影響なし（URLパス不変）

### 今後の課題
- ⏳ **フェーズ3**: データベースカラム名のタイポ修正（オプション、破壊的変更の可能性）
  - `chached` → `cached`
  - `is_shered` → `is_shared`
  - 慎重に計画が必要

### 推奨事項
1. **フェーズ2を優先実施**: エイリアス方式により非破壊的にPython側の命名規則を統一
2. **フェーズ3は慎重に検討**: データベース変更は必要に応じて実施
3. **段階的な移行**: 各フェーズを独立して実施し、検証を徹底
4. **本番環境への適用前に十分なテストを実施**

---

**最終更新**: 2026/02/10  
**作成者**: Cline (AI Assistant)
