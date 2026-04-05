import tkinter as tk
from tkinter import ttk, messagebox
import os
from src.project_manager import load_projects
from src.file_mover import move_file, skip_file


class FileDispatchDialog:
    """新規ファイル検知時に表示するポップアップダイアログ。

    master に永続的な Tk ルートを受け取り、Toplevel として表示する。
    Tk() は1プロセスで1回だけ生成する設計（watcher.py 側で管理）。
    """

    def __init__(self, master: tk.Tk, filepath: str):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.projects = load_projects()
        self.result = None

        self._build(master)

    def _build(self, master: tk.Tk):
        self.root = tk.Toplevel(master)
        self.root.title("ファイル振り分け")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.root.update_idletasks()
        w, h = 420, 300
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        pad = {"padx": 12, "pady": 6}

        tk.Label(self.root, text="新しいファイルを検知しました", font=("Helvetica", 13, "bold")).pack(**pad)
        tk.Label(
            self.root,
            text=self.filename,
            font=("Helvetica", 11),
            fg="#333",
            wraplength=380,
            justify="center",
        ).pack(**pad)

        tk.Label(self.root, text="移動先プロジェクトを選択してください", font=("Helvetica", 11)).pack(**pad)

        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=12)

        scrollbar = tk.Scrollbar(frame, orient="vertical")
        self.listbox = tk.Listbox(
            frame,
            yscrollcommand=scrollbar.set,
            font=("Helvetica", 11),
            selectmode="single",
            height=6,
        )
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)

        self._project_names = list(self.projects.keys())
        for name in self._project_names:
            path = self.projects[name]
            label = name if os.path.isdir(path) else f"⚠ {name}（パス不明）"
            self.listbox.insert(tk.END, label)

        if self.projects:
            self.listbox.select_set(0)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="振り分ける",
            width=14,
            bg="#4A90D9",
            fg="black",
            font=("Helvetica", 11),
            command=self._on_move,
        ).pack(side="left", padx=6)

        tk.Button(
            btn_frame,
            text="振り分けしない",
            width=14,
            font=("Helvetica", 11),
            command=self._on_skip,
        ).pack(side="left", padx=6)

        tk.Button(
            btn_frame,
            text="⚙ 設定",
            width=8,
            font=("Helvetica", 11),
            command=self._on_settings,
        ).pack(side="left", padx=6)

    def show(self) -> None:
        """ダイアログを表示し、ユーザーが閉じるまで待機する。

        Toplevel.wait_window() を使い、親の mainloop() を止めずに待機。
        """
        self.root.wait_window()

    def _on_move(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("未選択", "プロジェクトを選択してください。", parent=self.root)
            return
        project_name = self._project_names[selection[0]]
        project_dir = self.projects[project_name]

        if not os.path.isdir(project_dir):
            messagebox.showerror(
                "エラー",
                f"プロジェクトフォルダが見つかりません:\n{project_dir}",
                parent=self.root,
            )
            return

        try:
            dest = move_file(self.filepath, project_name, project_dir)
            messagebox.showinfo("完了", f"移動しました:\n{dest}", parent=self.root)
            self.result = (project_name, dest)
        except Exception as e:
            messagebox.showerror("エラー", str(e), parent=self.root)
        finally:
            self.root.destroy()

    def _on_skip(self):
        skip_file(self.filepath)
        self.root.destroy()

    def _on_settings(self):
        from src.settings_ui import SettingsWindow
        SettingsWindow(master=self.root).root.wait_window()
        self.projects = load_projects()
        self.listbox.delete(0, tk.END)
        self._project_names = list(self.projects.keys())
        for name in self._project_names:
            path = self.projects[name]
            label = name if os.path.isdir(path) else f"⚠ {name}（パス不明）"
            self.listbox.insert(tk.END, label)
        if self.projects:
            self.listbox.select_set(0)
