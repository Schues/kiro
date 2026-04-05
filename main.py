#!/usr/bin/env python3
"""
ダウンロードフォルダ自動振り分けアプリ

起動:
  python main.py           # 監視モード（通常起動）
  python main.py --settings  # 設定画面のみ起動
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    if "--settings" in sys.argv:
        from src.settings_ui import SettingsWindow
        SettingsWindow().show()
    else:
        from src.watcher import start_watching
        start_watching()
