#!/usr/bin/env python3
"""
Cline タスク履歴をエクスポートするスクリプト

フロー:
  1. 既存の cline-history.json を読み込む（永続データ）
  2. VS Code の Cline タスクディレクトリから新規タスクを取得
  3. JSON にマージ（重複排除・コスト更新）して保存
  4. JSON から cline-history.md を生成

使い方:
    python3 scripts/export-cline-history.py

出力:
    memory-bank/cline-history.json  (永続データ)
    memory-bank/cline-history.md    (表示用Markdown)
"""

import json
import os
import datetime
from pathlib import Path
from typing import Optional, List, Dict

CLINE_TASKS_DIR = os.path.expanduser(
    "~/.vscode-server/data/User/globalStorage/saoudrizwan.claude-dev/tasks"
)
CLINE_TASKS_DIR_ALT = os.path.expanduser(
    "~/.vscode/extensions/saoudrizwan.claude-dev-*/globalStorage/tasks"
)

BASE_DIR = Path(__file__).parent.parent / "memory-bank"
JSON_FILE = BASE_DIR / "cline-history.json"
MD_FILE = BASE_DIR / "cline-history.md"


def find_tasks_dir() -> Optional[str]:
    """Clineのタスクディレクトリを探す"""
    if os.path.isdir(CLINE_TASKS_DIR):
        return CLINE_TASKS_DIR

    import glob
    alt_dirs = glob.glob(CLINE_TASKS_DIR_ALT)
    if alt_dirs:
        return alt_dirs[0]

    return None


def load_history_json() -> List[Dict]:
    """既存のJSONファイルから履歴を読み込む"""
    if not JSON_FILE.exists():
        return []
    with open(JSON_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("tasks", [])


def save_history_json(tasks: List[Dict]) -> None:
    """履歴をJSONファイルに保存"""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data = {
        "updated_at": now,
        "task_count": len(tasks),
        "total_cost": round(sum(t.get("cost", 0) for t in tasks), 4),
        "tasks": tasks,
    }
    JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_task_info(task_dir: str, task_id: str) -> Optional[Dict]:
    """Clineのタスクディレクトリから情報を抽出"""
    ui_file = os.path.join(task_dir, "ui_messages.json")
    metadata_file = os.path.join(task_dir, "task_metadata.json")

    if not os.path.exists(ui_file):
        return None

    with open(ui_file, encoding="utf-8") as f:
        msgs = json.load(f)

    model_id = ""
    cline_version = ""
    if os.path.exists(metadata_file):
        with open(metadata_file, encoding="utf-8") as f:
            meta = json.load(f)
        if meta.get("model_usage"):
            model_id = meta["model_usage"][0].get("model_id", "")
        if meta.get("environment_history"):
            cline_version = meta["environment_history"][0].get("cline_version", "")

    title = ""
    total_cost = 0.0
    tokens_in = 0
    tokens_out = 0
    cache_writes = 0
    cache_reads = 0

    for m in msgs:
        if m.get("type") == "say" and m.get("say") == "task":
            title = m.get("text", "")[:200]
        if m.get("type") == "say" and m.get("say") == "api_req_started":
            try:
                info = json.loads(m.get("text", "{}"))
                # cost は各リクエスト単体のコスト → 合算する
                if info.get("cost"):
                    total_cost += info["cost"]
                if info.get("tokensIn"):
                    tokens_in += info["tokensIn"]
                if info.get("tokensOut"):
                    tokens_out += info["tokensOut"]
                if info.get("cacheWrites"):
                    cache_writes += info["cacheWrites"]
                if info.get("cacheReads"):
                    cache_reads += info["cacheReads"]
            except (json.JSONDecodeError, TypeError):
                pass

    ts = datetime.datetime.fromtimestamp(
        int(task_id) / 1000, tz=datetime.timezone.utc
    )

    return {
        "id": task_id,
        "date": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "cost": round(total_cost, 4),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cache_writes": cache_writes,
        "cache_reads": cache_reads,
        "model": model_id,
        "cline_version": cline_version,
    }


def fetch_new_tasks() -> List[Dict]:
    """VS CodeのClineタスクディレクトリから全タスクを取得"""
    tasks_dir = find_tasks_dir()
    if not tasks_dir:
        print("⚠ Clineのタスクディレクトリが見つかりません")
        return []

    print(f"タスクディレクトリ: {tasks_dir}")
    results = []
    for task_id in sorted(os.listdir(tasks_dir)):
        task_path = os.path.join(tasks_dir, task_id)
        if not os.path.isdir(task_path):
            continue
        info = extract_task_info(task_path, task_id)
        if info:
            results.append(info)
    return results


def merge_tasks(existing: List[Dict], new_tasks: List[Dict]) -> List[Dict]:
    """既存と新規をマージ（IDベースで重複排除、コスト更新）"""
    # IDをキーにした辞書
    task_map = {t["id"]: t for t in existing}

    added = 0
    updated = 0
    for task in new_tasks:
        tid = task["id"]
        if tid and tid not in task_map:
            task_map[tid] = task
            added += 1
        elif tid and tid in task_map:
            # コストが増えていたら更新
            if task["cost"] > task_map[tid].get("cost", 0):
                task_map[tid] = task
                updated += 1
        else:
            # IDなし（日時で重複チェック）
            date_exists = any(t["date"] == task["date"] for t in task_map.values())
            if not date_exists:
                task_map[task["date"]] = task
                added += 1

    merged = sorted(task_map.values(), key=lambda t: t.get("date", ""))
    print(f"既存: {len(existing)}件, 新規追加: {added}件, 更新: {updated}件, 合計: {len(merged)}件")
    return merged


def generate_markdown(tasks: List[Dict]) -> str:
    """JSONのタスクリストからMarkdownを生成"""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total_cost = sum(t.get("cost", 0) for t in tasks)
    models = sorted(set(t.get("model", "") for t in tasks if t.get("model")))
    versions = sorted(set(t.get("cline_version", "") for t in tasks if t.get("cline_version")))

    lines = [
        "# Cline タスク履歴",
        "",
        f"> 最終更新: {now}  ",
        "> このファイルは `scripts/export-cline-history.py` により自動生成されます。",
        "> データソース: `memory-bank/cline-history.json`",
        "",
        "| # | 日時 (UTC) | タスク | コスト | Tokens In | Tokens Out |",
        "|---|-----------|--------|--------|-----------|------------|",
    ]

    for i, t in enumerate(tasks, 1):
        cost = t.get("cost", 0)
        cost_str = f"${cost:.4f}" if cost else "N/A"
        # タイトルに改行が含まれている場合は1行目のみを使用
        title = t['title'].split('\n')[0].strip()
        lines.append(
            f"| {i} | {t['date']} | {title} | {cost_str} "
            f"| {t.get('tokens_in', 0):,} | {t.get('tokens_out', 0):,} |"
        )

    lines.extend([
        "",
        "## サマリー",
        "",
        f"- **タスク数**: {len(tasks)}",
        f"- **合計コスト**: ${total_cost:.4f}",
        f"- **モデル**: {', '.join(models) if models else 'N/A'}",
        f"- **Cline バージョン**: {', '.join(versions) if versions else 'N/A'}",
        "",
        "## 更新方法",
        "",
        "```bash",
        "python3 scripts/export-cline-history.py",
        "```",
        "",
        "## 注意事項",
        "",
        "- 永続データは `memory-bank/cline-history.json` で管理されています",
        "- VS Codeの履歴が消えても、JSONに記録済みのデータは保持されます",
        "- このMarkdownファイルはJSONから自動生成されるため、直接編集しないでください",
        "",
    ])

    return "\n".join(lines)


def main():
    # 1. 既存JSONから履歴を読み込む
    existing = load_history_json()
    print(f"既存JSON: {len(existing)}件")

    # 2. VS Codeから新規タスクを取得
    new_tasks = fetch_new_tasks()
    print(f"VS Code履歴: {len(new_tasks)}件")

    # 3. マージ
    merged = merge_tasks(existing, new_tasks)

    # 4. JSON保存
    save_history_json(merged)
    print(f"JSON保存: {JSON_FILE}")

    # 5. Markdown生成
    md = generate_markdown(merged)
    MD_FILE.write_text(md, encoding="utf-8")
    print(f"Markdown生成: {MD_FILE}")

    total = sum(t.get("cost", 0) for t in merged)
    print(f"合計コスト: ${total:.4f}")


if __name__ == "__main__":
    main()
