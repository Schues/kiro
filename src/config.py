import os
import json

_BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# プロジェクト設定ファイル
PROJECTS_FILE = os.path.join(_BASE_DIR, "projects.json")

# アプリ設定ファイル（監視フォルダなどを保存）
SETTINGS_FILE = os.path.join(_BASE_DIR, "settings.json")

# 多重起動防止用ロックファイル
LOCK_FILE = os.path.join(_BASE_DIR, "kiro.lock")

# ログファイル
LOG_FILE = os.path.join(_BASE_DIR, "move_log.csv")

# 除外する一時ファイルの拡張子
TEMP_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download", ".partial"}

# 日付フォルダのフォーマット
DATE_FORMAT = "%Y-%m-%d"

# デフォルト監視フォルダ
_DEFAULT_WATCH_FOLDER = os.path.expanduser("~/Downloads")


def _load_settings() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {}


def get_watch_folder() -> str:
    """設定ファイルから監視フォルダを取得する。未設定時は ~/Downloads を返す"""
    return _load_settings().get("watch_folder", _DEFAULT_WATCH_FOLDER)


def save_watch_folder(path: str) -> None:
    """監視フォルダをアトミックに設定ファイルへ保存する"""
    settings = _load_settings()
    settings["watch_folder"] = path
    tmp = SETTINGS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    os.replace(tmp, SETTINGS_FILE)
