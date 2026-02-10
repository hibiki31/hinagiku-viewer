# リファクタリング計画書

**日付**: 2026/02/10  
**対象**: hinagiku-viewer APIモジュール  
**目的**: FastAPIベストプラクティスに準拠した命名規則への統一

---

## 概要

本ドキュメントは、hinagiku-viewer APIモジュールにおける関数名・変数名のリファクタリング計画を記載します。
リファクタリングは3つのフェーズに分けて実施し、段階的に技術的負債を解消します。

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

## フェーズ2: データベースカラム名修正 ⚠️ **未実施**

### 目的
データベースのタイポを修正し、一貫性のある命名にする。

### 実施予定の変更

#### 2.1 データベースカラム名
| テーブル | 変更前 | 変更後 | 理由 |
|----------|--------|--------|------|
| `books` | `chached` | `cached` | タイポ修正（cached=キャッシュ済み） |
| `books` | `is_shered` | `is_shared` | タイポ修正（shared=共有済み） |

#### 2.2 必要な作業

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

#### 2.3 影響を受けるファイル
- `books/models.py` - モデル定義の修正
- `books/router.py` - クエリ・フィルタの修正
- `books/schemas.py` - スキーマ定義の修正
- `tasks/library_import.py` - カラム参照の修正
- その他、該当カラムを参照する全ファイル

#### 2.4 フロントエンド対応
```bash
# Vue 3フロントエンドで型定義を再生成
cd /workspace/vue
npx openapi-typescript https://hinav.hinagiku.me/api/openapi.json -o ./src/api.d.ts
```

**修正が必要なVue 3ファイル:**
- API呼び出しで `chached` を使用している箇所
- API呼び出しで `is_shered` を使用している箇所
- ストア、コンポーネント内の参照

### 影響範囲
- **外部API**: ⚠️ **破壊的変更** - レスポンスのプロパティ名が変更
- **既存クライアント**: 修正必要
- **データベース**: スキーマ変更（マイグレーション必要）

### リスク
- 🔴 **高**: 本番環境のデータベーススキーマ変更
- 🔴 **高**: フロントエンドの全面修正が必要
- 🟡 **中**: APIバージョンを上げることを推奨（3.0.0 → 4.0.0）

### 検証方法
1. 開発環境でマイグレーション実行
2. APIレスポンス確認
3. フロントエンド動作確認
4. 既存データの整合性確認

---

## フェーズ3: APIパラメータ名統一 ⚠️ **未実施**

### 目的
APIパラメータ名をPythonの命名規則（snake_case）に統一する。

### 実施予定の変更

#### 3.1 エンドポイントパラメータ名（books/router.py）
| 変更前 (camelCase) | 変更後 (snake_case) | エンドポイント |
|-------------------|-------------------|--------------|
| `fileNameLike` | `file_name_like` | `GET /api/books` |
| `authorLike` | `author_like` | `GET /api/books` |
| `titleLike` | `title_like` | `GET /api/books` |
| `fullText` | `full_text` | `GET /api/books` |
| `seriesId` | `series_id` | `GET /api/books` |
| `genreId` | `genre_id` | `GET /api/books` |
| `libraryId` | `library_id` | `GET /api/books` |
| `sortKey` | `sort_key` | `GET /api/books` |
| `sortDesc` | `sort_desc` | `GET /api/books` |

#### 3.2 エンドポイントパラメータ名（authors/router.py）
| 変更前 | 変更後 | エンドポイント |
|--------|--------|--------------|
| `isFavorite` | `is_favorite` | `GET /api/authors` |
| `nameLike` | `name_like` | `GET /api/authors` |

#### 3.3 スキーマプロパティ名（books/schemas.py）
| クラス | 変更前 | 変更後 |
|--------|--------|--------|
| `BookPut` | `series_no` | `series_number` |

#### 3.4 影響を受けるファイル
- `books/router.py` - 全エンドポイントのパラメータ定義
- `authors/router.py` - エンドポイントのパラメータ定義
- `books/schemas.py` - Pydanticスキーマ定義
- OpenAPI仕様書（自動生成）

#### 3.5 フロントエンド対応
**修正が必要な箇所:**
- `vue/src/pages/index.vue` - 書籍一覧のAPI呼び出し
- `vue/src/pages/books/[uuid].vue` - 書籍詳細のAPI呼び出し
- `vue/src/stores/readerState.ts` - 検索クエリの構築
- その他、該当APIを呼び出す全てのコンポーネント

### 影響範囲
- **外部API**: ⚠️ **破壊的変更** - クエリパラメータ名が変更
- **既存クライアント**: 全て修正必要
- **データベース**: 変更なし

### リスク
- 🔴 **高**: 全てのAPIクライアントに影響
- 🔴 **高**: Vue 3フロントエンドの広範囲な修正が必要
- 🟡 **中**: APIバージョンアップ必須（4.0.0 → 5.0.0 または 3.0.0 → 4.0.0）

### 検証方法
1. OpenAPI仕様書の確認
2. Swagger UIでのテスト
3. フロントエンド統合テスト
4. E2Eテスト

---

## フェーズ4: エンドポイント関数名の改善（オプション）

### 目的
エンドポイント関数名をより意味的に明確にする（内部のみ、URL不変）。

### 実施予定の変更

#### 4.1 関数名の改善（books/router.py）
| 変更前 | 変更後 | 理由 |
|--------|--------|------|
| `get_api_library()` | `list_libraries()` | RESTful命名規則 |
| `get_api_books()` | `list_books()` | RESTful命名規則 |
| `change_book_data()` | `update_books()` | 一貫性のある動詞 |
| `delete_book_data()` | `delete_book()` | シンプル化 |

#### 4.2 関数名の改善（users/router.py）
| 変更前 | 変更後 |
|--------|--------|
| `read_api_users()` | `list_users()` |
| `read_api_users_me()` | `get_current_user_info()` |
| `post_api_users()` | `create_user()` |

#### 4.3 関数名の改善（authors/router.py）
| 変更前 | 変更後 |
|--------|--------|
| `get_api_library()` | `list_authors()` |
| `post_api_books_uuid_authors()` | `add_book_author()` |
| `delete_api_books_uuid_authors()` | `remove_book_author()` |
| `patch_api_authors()` | `update_author()` |

#### 4.4 関数名の改善（tags/router.py）
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

#### 🟢 即時実施可能
1. ✅ **フェーズ1**: 非破壊的変更（完了）
2. ⏳ **フェーズ4**: エンドポイント関数名の改善（オプション）

#### 🟡 計画的に実施
3. ⏳ **フェーズ2**: データベースカラム名修正
   - マイグレーション準備
   - フロントエンド修正準備
   - バージョン番号決定（4.0.0推奨）
   - テスト計画策定

#### 🔴 慎重に実施
4. ⏳ **フェーズ3**: APIパラメータ名統一
   - APIバージョンアップ検討
   - 後方互換性維持戦略
   - 段階的移行計画

---

## ロールバック計画

### フェーズ1のロールバック
```bash
# Gitで前のコミットに戻す
git revert HEAD
```

### フェーズ2のロールバック
```bash
# マイグレーションのダウングレード
alembic downgrade -1

# コードのロールバック
git revert <commit-hash>
```

### フェーズ3のロールバック
```bash
# APIバージョンのロールバック
git revert <commit-hash>

# フロントエンドのロールバック
cd /workspace/vue
git revert <commit-hash>
```

---

## 参考資料

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

### 今後の課題
- ⏳ フェーズ2: データベースカラム名のタイポ修正（破壊的変更）
- ⏳ フェーズ3: APIパラメータ名の統一（破壊的変更）
- ⏳ フェーズ4: エンドポイント関数名の改善（非破壊的）

### 推奨事項
1. フェーズ2・3は別途スプリントを設けて計画的に実施
2. APIバージョンアップ（4.0.0）を検討
3. フロントエンド修正工数を事前に見積もる
4. 本番環境への適用前に十分なテストを実施

---

**最終更新**: 2026/02/10  
**作成者**: Cline (AI Assistant)
