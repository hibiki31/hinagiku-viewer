# 共通ユーティリティ
# DebugTimerはmixins/convertorに統一。後方互換性のため再エクスポート
from mixins.convertor import DebugTimer

__all__ = ["DebugTimer"]
