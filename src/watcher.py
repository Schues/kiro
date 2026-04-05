import os
import signal
import queue
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from src.config import get_watch_folder, TEMP_EXTENSIONS, LOCK_FILE
from src.ui import FileDispatchDialog

# バックグラウンドスレッド → メインスレッドへファイルパスを渡すキュー
_file_queue: queue.Queue = queue.Queue()


def _acquire_lock() -> bool:
    """
    ロックファイルを作成して多重起動を防止する。
    すでに起動中の場合は False を返す。
    """
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return False
        except (ValueError, ProcessLookupError, PermissionError):
            pass

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def _release_lock() -> None:
    """ロックファイルを削除する"""
    try:
        os.remove(LOCK_FILE)
    except FileNotFoundError:
        pass


class DownloadHandler(FileSystemEventHandler):
    """Downloads フォルダの新規ファイルを検知するハンドラ"""

    def __init__(self):
        super().__init__()
        self._pending = set()

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self._handle(event.dest_path)

    def _handle(self, filepath: str):
        ext = os.path.splitext(filepath)[1].lower()
        if ext in TEMP_EXTENSIONS:
            return
        if filepath in self._pending:
            return

        self._pending.add(filepath)

        def delayed():
            time.sleep(0.8)
            if os.path.exists(filepath):
                _file_queue.put(filepath)
            self._pending.discard(filepath)

        threading.Thread(target=delayed, daemon=True).start()


def start_watching():
    """監視を開始してブロックする"""
    if not _acquire_lock():
        print("[エラー] すでに起動中のインスタンスがあります。多重起動はできません。")
        return

    try:
        watch_folder = get_watch_folder()
        if not os.path.isdir(watch_folder):
            print(f"[エラー] 監視フォルダが存在しません: {watch_folder}")
            print("設定画面（python main.py --settings）で監視フォルダを変更してください。")
            return

        # Tk() は1プロセスで1回だけ生成し、アプリ終了まで保持する
        # withdraw() で非表示にし、after() でキューをポーリングしてダイアログを出す
        root = tk.Tk()
        root.withdraw()

        # ダイアログ表示中フラグ（同時に1つだけ表示する）
        _dialog_active = [False]

        def poll_queue():
            if not _dialog_active[0]:
                try:
                    filepath = _file_queue.get_nowait()
                    _dialog_active[0] = True
                    dialog = FileDispatchDialog(root, filepath)
                    dialog.show()
                    _dialog_active[0] = False
                except queue.Empty:
                    pass
            root.after(300, poll_queue)

        def shutdown(*_):
            observer.stop()
            root.quit()

        signal.signal(signal.SIGINT, shutdown)
        root.after(300, poll_queue)

        handler = DownloadHandler()
        observer = Observer()
        observer.schedule(handler, watch_folder, recursive=False)
        observer.start()
        print(f"監視開始: {watch_folder}")
        print("終了するには Ctrl+C を押してください。")

        root.mainloop()

        observer.join()

    finally:
        _release_lock()
