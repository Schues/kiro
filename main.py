#!/usr/bin/env python3
"""
kiro v1.2 - ダウンロードフォルダ自動振り分けアプリ

起動: python main.py
配布: build/ 以下のスクリプトで .app / .exe を生成
"""
import os
import sys
import queue
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(__file__))

from src.watcher import Watcher, acquire_lock, release_lock
from src.tray import TrayApp
from src.ui import FileDispatchDialog


def main():
    # --- 多重起動チェック ---
    if not acquire_lock():
        _root = tk.Tk()
        _root.withdraw()
        messagebox.showerror("kiro", "すでに起動中のインスタンスがあります。\nタスクバー／メニューバーのアイコンを確認してください。")
        _root.destroy()
        return

    try:
        watcher = Watcher()

        # tkinter ルートはメインスレッドに常駐（非表示）
        root = tk.Tk()
        root.withdraw()

        # ダイアログ多重表示防止フラグ
        _dialog_active = [False]

        def poll_queue():
            """300ms ごとにキューを確認してダイアログを表示する。"""
            if not _dialog_active[0]:
                try:
                    filepath = watcher.get_file_queue().get_nowait()
                    _dialog_active[0] = True
                    dialog = FileDispatchDialog(root, filepath)
                    dialog.show()
                    _dialog_active[0] = False
                except queue.Empty:
                    pass
            root.after(300, poll_queue)

        # --- トレイコールバック（トレイのワーカースレッドから呼ばれる） ---

        def on_start():
            ok, msg = watcher.start()
            tray.update_status(watcher.is_running)
            if not ok:
                root.after(0, lambda: messagebox.showwarning("kiro", msg))

        def on_stop():
            watcher.stop()
            tray.update_status(watcher.is_running)

        def on_settings():
            # tkinter 操作はメインスレッドで行う
            root.after(0, _open_settings)

        def _open_settings():
            from src.settings_ui import SettingsWindow
            win = SettingsWindow(master=root)
            win.root.wait_window()

        def on_quit():
            watcher.stop()
            root.after(0, root.quit)

        # --- トレイ起動 ---
        tray = TrayApp(on_start, on_stop, on_settings, on_quit)
        tray.run_detached()

        # 起動直後に自動で監視開始
        on_start()

        root.after(300, poll_queue)
        root.mainloop()

    finally:
        release_lock()


if __name__ == "__main__":
    main()
