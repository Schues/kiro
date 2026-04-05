import json
import os
import shutil
from datetime import datetime
from src.config import PROJECTS_FILE


def load_projects() -> dict:
    """projects.json を読み込んで返す。破損時はバックアップを作成して空の辞書を返す"""
    if not os.path.exists(PROJECTS_FILE):
        return {}
    try:
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("projects.json のフォーマットが不正です")
        return data
    except (json.JSONDecodeError, ValueError):
        backup = PROJECTS_FILE + ".bak_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(PROJECTS_FILE, backup)
        print(f"[警告] projects.json が破損していたためバックアップを作成しました: {backup}")
        return {}


def save_projects(projects: dict) -> None:
    """projects.json にアトミックに書き込む"""
    tmp = PROJECTS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PROJECTS_FILE)
