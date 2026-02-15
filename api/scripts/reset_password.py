#!/usr/bin/env python3
"""
ユーザーのパスワードを再設定する運用スクリプト

使用方法:
    python3 scripts/reset_password.py <user_id> <new_password>

例:
    python3 scripts/reset_password.py admin newpassword123
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mixins.log import setup_logger
from settings import SQLALCHEMY_DATABASE_URL
from users.models import UserModel

# pwdlibを使用したパスワードハッシュ化（auth/router.pyと同じ設定）
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

logger = setup_logger(__name__)

# パスワードハッシュ化の設定（auth/router.pyと同一）
pwd_context = PasswordHash([Argon2Hasher()])


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化する

    Args:
        password: ハッシュ化するパスワード

    Returns:
        ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)


def reset_user_password(user_id: str, new_password: str) -> bool:
    """
    指定されたユーザーのパスワードを再設定する

    Args:
        user_id: パスワードを再設定するユーザーID
        new_password: 新しいパスワード

    Returns:
        成功した場合True、失敗した場合False
    """
    try:
        # データベース接続
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        with Session(engine) as session:
            # ユーザーを検索
            user = session.query(UserModel).filter(UserModel.id == user_id).first()
            
            if user is None:
                logger.error(f"ユーザーが見つかりません: {user_id}")
                return False
            
            # パスワードをハッシュ化して更新
            hashed_password = get_password_hash(new_password)
            user.password = hashed_password
            
            # 変更をコミット
            session.commit()
            
            logger.info(f"ユーザー '{user_id}' のパスワードを正常に再設定しました")
            return True
            
    except Exception as e:
        logger.error(f"パスワード再設定中にエラーが発生しました: {e}")
        return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="ユーザーのパスワードを再設定する運用スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 scripts/reset_password.py admin newpassword123
  python3 scripts/reset_password.py user001 secure_pass_456
        """
    )
    
    parser.add_argument(
        "user_id",
        type=str,
        help="パスワードを再設定するユーザーID"
    )
    
    parser.add_argument(
        "new_password",
        type=str,
        help="新しいパスワード"
    )
    
    args = parser.parse_args()
    
    # 入力値の検証
    if not args.user_id or not args.user_id.strip():
        logger.error("ユーザーIDが空です")
        sys.exit(1)
    
    if not args.new_password or not args.new_password.strip():
        logger.error("新しいパスワードが空です")
        sys.exit(1)
    
    if len(args.new_password) < 4:
        logger.warning("パスワードが短すぎます（推奨: 8文字以上）")
    
    # パスワード再設定を実行
    logger.info(f"ユーザー '{args.user_id}' のパスワード再設定を開始します")
    
    success = reset_user_password(args.user_id, args.new_password)
    
    if success:
        print(f"✓ ユーザー '{args.user_id}' のパスワードを正常に再設定しました")
        sys.exit(0)
    else:
        print(f"✗ パスワードの再設定に失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
