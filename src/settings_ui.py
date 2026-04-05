import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from src.project_manager import load_projects, save_projects
from src.config import get_watch_folder, save_watch_folder


class SettingsWindow:
    """プロジェクト設定を管理するGUIウィンドウ"""

    def __init__(self, master=None):
        self.projects = load_projects()

        self.root = tk.Toplevel(master) if master else tk.Tk()
        self.root.title("設定 - プロジェクト管理")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        w, h = 560, 470
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        self._build()
        self._refresh_list()

    def _build(self):
        # --- プロジェクト一覧 ---
        list_frame = tk.LabelFrame(self.root, text="プロジェクト一覧", font=("Helvetica", 11), padx=8, pady=8)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        cols = ("name", "path")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=8, selectmode="browse")
        self.tree.heading("name", text="プロジェクト名")
        self.tree.heading("path", text="フォルダパス")
        self.tree.column("name", width=150, anchor="w")
        self.tree.column("path", width=340, anchor="w")

        sb = tk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # --- 入力フォーム ---
        form_frame = tk.LabelFrame(self.root, text="プロジェクトを追加 / 編集", font=("Helvetica", 11), padx=8, pady=8)
        form_frame.pack(fill="x", padx=12, pady=4)

        tk.Label(form_frame, text="名前:", font=("Helvetica", 11), width=6, anchor="e").grid(row=0, column=0, padx=4, pady=4)
        self.name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.name_var, font=("Helvetica", 11), width=20).grid(row=0, column=1, padx=4, pady=4, sticky="w")

        tk.Label(form_frame, text="パス:", font=("Helvetica", 11), width=6, anchor="e").grid(row=1, column=0, padx=4, pady=4)
        self.path_var = tk.StringVar()
        path_entry = tk.Entry(form_frame, textvariable=self.path_var, font=("Helvetica", 11), width=36)
        path_entry.grid(row=1, column=1, padx=4, pady=4, sticky="w")
        tk.Button(form_frame, text="参照…", font=("Helvetica", 10), command=self._browse).grid(row=1, column=2, padx=4)

        # --- 操作ボタン ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="追加 / 更新", width=12, bg="#4A90D9",
                  font=("Helvetica", 11), command=self._on_save).pack(side="left", padx=6)
        tk.Button(btn_frame, text="削除", width=10,
                  font=("Helvetica", 11), command=self._on_delete).pack(side="left", padx=6)
        tk.Button(btn_frame, text="クリア", width=10,
                  font=("Helvetica", 11), command=self._clear_form).pack(side="left", padx=6)
        tk.Button(btn_frame, text="閉じる", width=10,
                  font=("Helvetica", 11), command=self.root.destroy).pack(side="left", padx=6)

        # --- 監視フォルダ設定 ---
        watch_frame = tk.LabelFrame(self.root, text="監視フォルダ設定", font=("Helvetica", 11), padx=8, pady=8)
        watch_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.watch_var = tk.StringVar(value=get_watch_folder())
        watch_entry = tk.Entry(watch_frame, textvariable=self.watch_var, font=("Helvetica", 11), width=38)
        watch_entry.grid(row=0, column=0, padx=4, pady=4, sticky="w")
        tk.Button(watch_frame, text="参照…", font=("Helvetica", 10),
                  command=self._browse_watch).grid(row=0, column=1, padx=4)
        tk.Button(watch_frame, text="保存", width=8, bg="#4A90D9",
                  font=("Helvetica", 10), command=self._on_save_watch).grid(row=0, column=2, padx=4)

    def _refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for name, path in self.projects.items():
            self.tree.insert("", "end", values=(name, path))

    def _on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        name, path = self.tree.item(selected[0], "values")
        self.name_var.set(name)
        self.path_var.set(path)

    def _browse(self):
        folder = filedialog.askdirectory(title="プロジェクトフォルダを選択", parent=self.root)
        if folder:
            self.path_var.set(folder)
            # 名前が空なら末尾フォルダ名を自動入力
            if not self.name_var.get():
                self.name_var.set(os.path.basename(folder))

    def _browse_watch(self):
        folder = filedialog.askdirectory(title="監視フォルダを選択", parent=self.root)
        if folder:
            self.watch_var.set(folder)

    def _on_save_watch(self):
        path = self.watch_var.get().strip()
        if not path:
            messagebox.showwarning("入力エラー", "フォルダパスを入力してください。", parent=self.root)
            return
        if not os.path.isdir(path):
            messagebox.showerror("エラー", f"フォルダが存在しません:\n{path}", parent=self.root)
            return
        save_watch_folder(path)
        messagebox.showinfo("完了", f"監視フォルダを保存しました。\n次回起動から反映されます:\n{path}", parent=self.root)

    def _on_save(self):
        name = self.name_var.get().strip()
        path = self.path_var.get().strip()

        if not name:
            messagebox.showwarning("入力エラー", "プロジェクト名を入力してください。", parent=self.root)
            return
        if not path:
            messagebox.showwarning("入力エラー", "フォルダパスを入力してください。", parent=self.root)
            return
        if not os.path.isdir(path):
            if not messagebox.askyesno("確認", f"フォルダが存在しません。\n{path}\n\nそのまま保存しますか？", parent=self.root):
                return

        self.projects[name] = path
        save_projects(self.projects)
        self._refresh_list()
        self._clear_form()

    def _on_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("未選択", "削除するプロジェクトを選択してください。", parent=self.root)
            return
        name, _ = self.tree.item(selected[0], "values")
        if messagebox.askyesno("確認", f"「{name}」を削除しますか？", parent=self.root):
            self.projects.pop(name, None)
            save_projects(self.projects)
            self._refresh_list()
            self._clear_form()

    def _clear_form(self):
        self.name_var.set("")
        self.path_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def show(self):
        self.root.mainloop()
