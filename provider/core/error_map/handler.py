from __future__ import annotations
from .taxonomy import ProviderError
from typing import Final

USER_SAFE: Final = {
    "AuthFailed": "認証に失敗しました。APIキーや権限を確認してください。",
    "RateLimited": "混雑により待機が必要です。しばらくしてから再実行してください。",
    "ProviderDown": "提供元で障害が発生しています。時間を置いて再実行してください。",
    "Timeout": "応答がタイムアウトしました。入力を短くするか再試行してください。",
    "BadInput": "入力形式に問題がありました。入力内容の見直しをお願いします。",
    "QuotaExceeded": "利用上限に達しています。上限の拡張や時間を置いての再実行をご検討ください。",
    "SafetyBlocked": "安全性ポリシーによりブロックされました。",
    "Unknown": "不明なエラーが発生しました。"
}

def user_message(e: ProviderError) -> str:
    return USER_SAFE.get(e.code, USER_SAFE["Unknown"])
