import os
import shutil
import csv
from datetime import datetime
from src.config import DATE_FORMAT, LOG_FILE


def move_file(src_path: str, project_name: str, project_dir: str) -> str:
    """
    ファイルをプロジェクトフォルダ配下の日付フォルダへ移動する。
    移動先パスを返す。
    """
    date_str = datetime.now().strftime(DATE_FORMAT)
    dest_dir = os.path.join(project_dir, date_str)

    filename = os.path.basename(src_path)
    dest_path = os.path.join(dest_dir, filename)

    # 移動前にフォルダが既存かどうかを記録（失敗時のロールバック用）
    dest_dir_existed = os.path.isdir(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    # 同名ファイルが存在する場合はリネーム
    if os.path.exists(dest_path):
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%H%M%S")
        dest_path = os.path.join(dest_dir, f"{name}_{timestamp}{ext}")

    try:
        shutil.move(src_path, dest_path)
    except Exception:
        # 移動失敗時、このコードで作成した空フォルダを削除して痕跡を残さない
        if not dest_dir_existed and os.path.isdir(dest_dir) and not os.listdir(dest_dir):
            os.rmdir(dest_dir)
        raise

    _write_log(filename, dest_path, project_name)
    return dest_path


def skip_file(src_path: str) -> None:
    """振り分けしない場合のログ記録"""
    filename = os.path.basename(src_path)
    _write_log(filename, src_path, "（振り分けなし）")


def _write_log(filename: str, dest_path: str, project_name: str) -> None:
    """CSV ログに1行追記する"""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["datetime", "filename", "destination", "project"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            filename,
            dest_path,
            project_name,
        ])
