import os
import queue
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import get_watch_folder, TEMP_EXTENSIONS, LOCK_FILE

_file_queue: queue.Queue = queue.Queue()


def _is_pid_running(pid: int) -> bool:
    try:
        import psutil
        return psutil.pid_exists(pid)
    except ImportError:
        # psutil 未インストール時のフォールバック（macOS/Linux のみ有効）
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, OSError):
            return False


def acquire_lock() -> bool:
    """ロックファイルを作成して多重起動を防止する。すでに起動中なら False を返す。"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            if _is_pid_running(pid):
                return False
        except (ValueError, OSError):
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def release_lock() -> None:
    """ロックファイルを削除する。"""
    try:
        os.remove(LOCK_FILE)
    except FileNotFoundError:
        pass


class DownloadHandler(FileSystemEventHandler):
    """Downloads フォルダの新規ファイルを検知するハンドラ。"""

    def __init__(self):
        super().__init__()
        self._pending = set()

    def on_created(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._handle(event.dest_path)

    def _handle(self, filepath: str):
        ext = os.path.splitext(filepath)[1].lower()
        if ext in TEMP_EXTENSIONS or filepath in self._pending:
            return
        self._pending.add(filepath)

        def delayed():
            time.sleep(0.8)
            if os.path.exists(filepath):
                _file_queue.put(filepath)
            self._pending.discard(filepath)

        threading.Thread(target=delayed, daemon=True).start()


class Watcher:
    """ファイル監視の開始・停止を管理するクラス。スレッドセーフ。"""

    def __init__(self):
        self._observer = None
        self._running = False
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> tuple[bool, str]:
        """監視を開始する。(success: bool, message: str) を返す。"""
        with self._lock:
            if self._running:
                return False, "すでに監視中です"
            watch_folder = get_watch_folder()
            if not os.path.isdir(watch_folder):
                return False, f"監視フォルダが存在しません: {watch_folder}"
            handler = DownloadHandler()
            self._observer = Observer()
            self._observer.schedule(handler, watch_folder, recursive=False)
            self._observer.start()
            self._running = True
            return True, watch_folder

    def stop(self) -> None:
        """監視を停止する（ノンブロッキング）。"""
        with self._lock:
            if not self._running:
                return
            obs = self._observer
            self._observer = None
            self._running = False

        def _do_stop():
            obs.stop()
            obs.join()

        threading.Thread(target=_do_stop, daemon=True).start()

    @staticmethod
    def get_file_queue() -> queue.Queue:
        return _file_queue
