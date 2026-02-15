"""システム設定ユーティリティ関数"""
import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from system.models import SystemSettingsModel


def get_setting(db: Session, key: str, default: Any = None) -> Any:
    """
    設定値を取得（型変換済み）

    Args:
        db: DBセッション
        key: 設定キー
        default: デフォルト値（設定が存在しない場合）

    Returns:
        型変換された設定値、または default

    Example:
        >>> quality = get_setting(db, 'thumbnail_quality', default=85)
        >>> isinstance(quality, int)
        True
    """
    setting = db.query(SystemSettingsModel).filter(SystemSettingsModel.key == key).first()
    if not setting:
        return default

    # 型変換
    try:
        if setting.data_type == 'int':
            result = int(setting.value)
        elif setting.data_type == 'float':
            result = float(setting.value)
        elif setting.data_type == 'bool':
            result = setting.value.lower() in ('true', '1', 'yes')
        elif setting.data_type == 'json':
            result = json.loads(setting.value)
        else:
            result = setting.value
        return result
    except (ValueError, json.JSONDecodeError):
        # 型変換に失敗した場合はデフォルト値を返す
        return default


def set_setting(db: Session, key: str, value: Any, user_id: str | None = None) -> SystemSettingsModel:
    """
    設定値を更新

    Args:
        db: DBセッション
        key: 設定キー
        value: 設定値（自動的に文字列に変換）
        user_id: 更新者のユーザーID

    Returns:
        更新された SystemSettingsModel

    Raises:
        ValueError: 指定されたキーの設定が存在しない場合
    """
    setting = db.query(SystemSettingsModel).filter(SystemSettingsModel.key == key).first()
    if not setting:
        raise ValueError(f"設定キー '{key}' が見つかりません")

    # 値を文字列に変換
    if isinstance(value, bool):
        setting.value = 'true' if value else 'false'
    elif isinstance(value, (dict, list)):
        setting.value = json.dumps(value, ensure_ascii=False)
    else:
        setting.value = str(value)

    setting.updated_at = datetime.now()
    setting.updated_by = user_id

    db.commit()
    db.refresh(setting)
    return setting


def get_settings_by_category(db: Session, category: str, include_private: bool = False) -> dict[str, Any]:
    """
    カテゴリ別に設定を取得

    Args:
        db: DBセッション
        category: カテゴリ名
        include_private: 非公開設定も含めるか（管理者用）

    Returns:
        {key: value} 形式の辞書（型変換済み）
    """
    query = db.query(SystemSettingsModel).filter(SystemSettingsModel.category == category)

    if not include_private:
        query = query.filter(SystemSettingsModel.is_public.is_(True))

    settings = query.all()

    result = {}
    for setting in settings:
        result[setting.key] = get_setting(db, setting.key)

    return result


def get_all_settings(db: Session, include_private: bool = False) -> dict[str, Any]:
    """
    全設定を取得

    Args:
        db: DBセッション
        include_private: 非公開設定も含めるか（管理者用）

    Returns:
        {key: value} 形式の辞書（型変換済み）
    """
    query = db.query(SystemSettingsModel)

    if not include_private:
        query = query.filter(SystemSettingsModel.is_public.is_(True))

    settings = query.all()

    result = {}
    for setting in settings:
        result[setting.key] = get_setting(db, setting.key)

    return result
