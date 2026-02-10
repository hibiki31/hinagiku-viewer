from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mixins.database import get_db
from mixins.log import setup_logger
from system.models import SystemSettingsModel
from system.schemas import (
    SystemSettingBulkUpdateSchema,
    SystemSettingCreateSchema,
    SystemSettingSchema,
    SystemSettingsListResponse,
    SystemSettingValueSchema,
)
from system.utility import get_all_settings, get_settings_by_category, set_setting
from users.models import UserModel
from users.router import get_current_user

logger = setup_logger(__name__)

app = APIRouter(
    prefix="/api/system",
    tags=["System"],
)


@app.get("/settings", response_model=SystemSettingsListResponse)
async def list_settings(
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    システム設定一覧を取得
    
    - 管理者: 全設定を取得可能
    - 一般ユーザー: is_public=true の設定のみ取得可能
    - category パラメータでフィルタリング可能
    """
    include_private = current_user.is_admin

    if category:
        query = db.query(SystemSettingsModel).filter(SystemSettingsModel.category == category)
    else:
        query = db.query(SystemSettingsModel)

    if not include_private:
        query = query.filter(SystemSettingsModel.is_public.is_(True))

    settings = query.order_by(SystemSettingsModel.category, SystemSettingsModel.key).all()

    logger.info(f"ユーザー {current_user.id} が設定一覧を取得: {len(settings)}件")

    return SystemSettingsListResponse(
        settings=[SystemSettingSchema.model_validate(s) for s in settings],
        total=len(settings)
    )


@app.get("/settings/{key}", response_model=SystemSettingSchema)
async def get_setting_by_key(
    key: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    個別設定を取得
    
    - 管理者: 全設定を取得可能
    - 一般ユーザー: is_public=true の設定のみ取得可能
    """
    setting = db.query(SystemSettingsModel).filter(SystemSettingsModel.key == key).first()

    if not setting:
        raise HTTPException(status_code=404, detail=f"設定キー '{key}' が見つかりません")

    # 一般ユーザーは公開設定のみ取得可能
    if not current_user.is_admin and not setting.is_public:
        raise HTTPException(status_code=403, detail="この設定にアクセスする権限がありません")

    logger.info(f"ユーザー {current_user.id} が設定 '{key}' を取得")

    return SystemSettingSchema.model_validate(setting)


@app.post("/settings", response_model=SystemSettingSchema)
async def create_setting(
    data: SystemSettingCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    新規設定を作成（管理者のみ）
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="管理者権限が必要です")

    # 重複チェック
    existing = db.query(SystemSettingsModel).filter(SystemSettingsModel.key == data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"設定キー '{data.key}' は既に存在します")

    # 新規作成
    new_setting = SystemSettingsModel(
        key=data.key,
        value=data.value,
        data_type=data.data_type,
        description=data.description,
        category=data.category,
        is_public=data.is_public,
        updated_by=current_user.id,
    )

    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)

    logger.info(f"ユーザー {current_user.id} が設定 '{data.key}' を作成")

    return SystemSettingSchema.model_validate(new_setting)


@app.put("/settings/{key}", response_model=SystemSettingSchema)
async def update_setting(
    key: str,
    data: SystemSettingValueSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    設定を更新（管理者のみ）
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="管理者権限が必要です")

    try:
        updated_setting = set_setting(db, key, data.value, user_id=current_user.id)
        logger.info(f"ユーザー {current_user.id} が設定 '{key}' を更新: {data.value}")
        return SystemSettingSchema.model_validate(updated_setting)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.delete("/settings/{key}")
async def delete_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    設定を削除（管理者のみ）
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="管理者権限が必要です")

    setting = db.query(SystemSettingsModel).filter(SystemSettingsModel.key == key).first()

    if not setting:
        raise HTTPException(status_code=404, detail=f"設定キー '{key}' が見つかりません")

    db.delete(setting)
    db.commit()

    logger.info(f"ユーザー {current_user.id} が設定 '{key}' を削除")

    return {"message": f"設定 '{key}' を削除しました"}


@app.post("/settings/bulk")
async def bulk_update_settings(
    data: SystemSettingBulkUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    設定を一括更新（管理者のみ）
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="管理者権限が必要です")

    updated_count = 0
    errors = []

    for key, value in data.settings.items():
        try:
            set_setting(db, key, value, user_id=current_user.id)
            updated_count += 1
        except ValueError as e:
            errors.append({"key": key, "error": str(e)})

    logger.info(f"ユーザー {current_user.id} が {updated_count}件の設定を一括更新")

    if errors:
        return {
            "message": f"{updated_count}件の設定を更新しました（エラー: {len(errors)}件）",
            "updated": updated_count,
            "errors": errors
        }

    return {
        "message": f"{updated_count}件の設定を更新しました",
        "updated": updated_count
    }


@app.get("/settings/category/{category}")
async def get_settings_by_category_endpoint(
    category: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    カテゴリ別に設定を取得（型変換済みの値）
    
    - 管理者: 全設定を取得可能
    - 一般ユーザー: is_public=true の設定のみ取得可能
    """
    include_private = current_user.is_admin
    settings = get_settings_by_category(db, category, include_private=include_private)

    logger.info(f"ユーザー {current_user.id} がカテゴリ '{category}' の設定を取得: {len(settings)}件")

    return settings


@app.get("/settings/all/values")
async def get_all_settings_values(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    全設定を取得（型変換済みの値）
    
    - 管理者: 全設定を取得可能
    - 一般ユーザー: is_public=true の設定のみ取得可能
    """
    include_private = current_user.is_admin
    settings = get_all_settings(db, include_private=include_private)

    logger.info(f"ユーザー {current_user.id} が全設定を取得: {len(settings)}件")

    return settings
