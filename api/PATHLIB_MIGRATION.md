# pathlibへの移行分析

## 現状

ruffによるコード品質チェックで102個のPTH系エラーが検出されています。これらはすべてpathlibへの移行を推奨するコードスタイルの提案です。

## エラー分類

| ルール | 件数 | 内容 | 優先度 |
|--------|------|------|--------|
| PTH122 | 20 | `os.path.splitext` → `Path.suffix` | 中 |
| PTH123 | 18 | `open()` → `Path.open()` | 低 |
| PTH103 | 14 | `os.makedirs` → `Path.mkdir()` | 高 |
| PTH119 | 14 | `os.path.basename` → `Path.name` | 中 |
| PTH207 | 9 | `glob.glob` → `Path.glob()` | 中 |
| PTH202 | 6 | `os.path.getsize` → `Path.stat().st_size` | 低 |
| PTH120 | 5 | `os.path.dirname` → `Path.parent` | 中 |
| PTH110 | 4 | `os.path.exists` → `Path.exists()` | 高 |
| PTH118 | 3 | `os.path.join` → `/` 演算子 | 高 |
| PTH101 | 2 | `os.chmod` → `Path.chmod()` | 低 |
| PTH102 | 2 | `os.mkdir` → `Path.mkdir()` | 高 |
| PTH107 | 2 | `os.remove` → `Path.unlink()` | 中 |
| PTH204 | 2 | `os.path.getmtime` → `Path.stat().st_mtime` | 低 |
| PTH208 | 1 | `os.listdir` → `Path.iterdir()` | 中 |

## pathlibのメリット

### 1. コードの可読性向上
```python
# Before
file_path = os.path.join(DATA_ROOT, "book_cache", book_uuid, f"{height}_{page}.jpg")

# After
file_path = Path(DATA_ROOT) / "book_cache" / book_uuid / f"{height}_{page}.jpg"
```

### 2. オブジェクト指向的なAPI
```python
# Before
if os.path.exists(file_path):
    size = os.path.getsize(file_path)
    name = os.path.basename(file_path)

# After
path = Path(file_path)
if path.exists():
    size = path.stat().st_size
    name = path.name
```

### 3. クロスプラットフォーム対応
pathlibは自動的にOSに応じたパス区切り文字を使用します。

### 4. 型安全性
pathlibはPathオブジェクトとして扱われるため、型チェックが容易です。

## pathlibのデメリット

### 1. Python 3.4以降が必要
- 本プロジェクトはPython 3.8以降を対象としているため問題なし

### 2. 学習コスト
- チームメンバーがpathlibに慣れる必要がある

### 3. 大規模な変更
- 102箇所の変更が必要
- テストが必要

### 4. 一部の操作はos.pathより冗長
```python
# splitext の場合
# Before: os.path.splitext(path)[1]
# After: Path(path).suffix  # より簡潔
```

## 推奨される移行戦略

### オプション1: 段階的移行（推奨）

**フェーズ1: 高優先度の移行（即座に実施可能）**
- PTH103 (os.makedirs) → 14箇所
- PTH110 (os.path.exists) → 4箇所
- PTH102 (os.mkdir) → 2箇所
- PTH118 (os.path.join) → 3箇所

**合計: 23箇所 (最も安全性とメンテナンス性が向上する部分)**

**フェーズ2: 中優先度の移行**
- PTH122 (os.path.splitext) → 20箇所
- PTH119 (os.path.basename) → 14箇所
- PTH207 (glob.glob) → 9箇所
- PTH120 (os.path.dirname) → 5箇所
- PTH107 (os.remove) → 2箇所
- PTH208 (os.listdir) → 1箇所

**合計: 51箇所**

**フェーズ3: 低優先度の移行（任意）**
- PTH123 (open()) → 18箇所（現状でも問題なし）
- PTH202 (os.path.getsize) → 6箇所
- PTH101 (os.chmod) → 2箇所
- PTH204 (os.path.getmtime) → 2箇所

**合計: 28箇所**

### オプション2: 全面移行

一度にすべての102箇所を移行。リスクが高いが、一貫性が保たれる。

### オプション3: 現状維持

pathlibへの移行を行わず、現状のos/glob APIを使い続ける。
- 既存コードは問題なく動作している
- チームがos/globに慣れている場合は合理的

## 推奨事項

**推奨: オプション1（段階的移行）のフェーズ1のみ実施**

理由:
1. **最小限のリスク**: 23箇所のみの変更で安全性が向上
2. **即座のメリット**: ディレクトリ作成とパス操作の安全性が向上
3. **後方互換性**: 既存のコードと共存可能
4. **テスト負荷**: 限定的な範囲でテストが容易

フェーズ1で変更する内容:
```python
# PTH103: os.makedirs → Path.mkdir
os.makedirs(path, exist_ok=True)
→ Path(path).mkdir(parents=True, exist_ok=True)

# PTH110: os.path.exists → Path.exists
if os.path.exists(file_path):
→ if Path(file_path).exists():

# PTH118: os.path.join → / 演算子
path = os.path.join(root, "sub", "file.txt")
→ path = Path(root) / "sub" / "file.txt"
```

## 次のステップ

1. **フェーズ1の実装を検討するか決定**
2. **実装する場合、テストケースを準備**
3. **変更を別ブランチで実施**
4. **テスト実行後にマージ**

## pyproject.toml設定の推奨

現状維持を選択する場合、PTHルールを無視することも可能:
```toml
ignore = [
    # ... 既存のignore
    "PTH",  # pathlibへの移行を強制しない
]
```

ただし、新規コードではpathlibの使用を推奨します。
