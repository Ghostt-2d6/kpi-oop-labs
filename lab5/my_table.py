import tkinter as tk
from tkinter import ttk


class MyTable:
    COLUMNS = ("num", "name", "x1", "y1", "x2", "y2")
    HEADERS = {
        "num": ("№", 45),
        "name": ("Назва", 180),
        "x1": ("x1", 80),
        "y1": ("y1", 80),
        "x2": ("x2", 80),
        "y2": ("y2", 80)
    }

    def __init__(self, master, on_select_callback=None, on_delete_callback=None, on_close_callback=None):
        self.master = master
        self.on_select_callback = on_select_callback
        self.on_delete_callback = on_delete_callback
        self.on_close_callback = on_close_callback
        self.window: tk.Toplevel | None = None
        self.tree: ttk.Treeview | None = None
        self._rows: list[tuple[str, int, int, int, int]] = []

    def is_open(self):
        return self.window is not None and bool(self.window.winfo_exists())

    def open_window(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            return
        window = tk.Toplevel(self.master)
        window.title("Таблиця об’єктів — Lab5")
        window.geometry("580x360")
        window.minsize(480, 260)
        window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.window = window

        table_frame = tk.Frame(window)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        tree = ttk.Treeview(table_frame, columns=self.COLUMNS, show="headings", selectmode="browse")
        for col in self.COLUMNS:
            heading_text, width = self.HEADERS[col]
            tree.heading(col, text=heading_text)
            tree.column(col, width=width, minwidth=40, anchor=tk.W if col == "name" else tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        tree.bind("<Delete>", self.delete_selected)
        self.tree = tree

        bottom_bar = tk.Frame(window)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(4, 8))

        delete_btn = tk.Button(bottom_bar, text="Вилучити вибраний", font=("Segoe UI", 9), padx=10, pady=3, command=self.delete_selected)
        delete_btn.pack(side=tk.LEFT)

        hint_lbl = tk.Label(bottom_bar, text="Клік по рядку — виділення на полотні; Delete — вилучення", font=("Segoe UI", 9), fg="#475569")
        hint_lbl.pack(side=tk.RIGHT)
        self._refresh_tree()

    def close_window(self):
        if self.window is not None:
            if self.window.winfo_exists():
                self.window.destroy()
        self.window = None
        self.tree = None
        if self.on_select_callback is not None:
            self.on_select_callback(None)
        if self.on_close_callback is not None:
            self.on_close_callback()

    def toggle_window(self):
        if self.is_open():
            self.close_window()
        else:
            self.open_window()

    def set_rows(self, rows):
        self._rows = list(rows)
        self._refresh_tree()

    def add_row(self, name, x1, y1, x2, y2):
        self._rows.append((name, x1, y1, x2, y2))
        if self.is_open() and self.tree is not None:
            self.tree.insert("", tk.END, values=(len(self._rows), name, x1, y1, x2, y2))

    def clear_rows(self):
        self._rows.clear()
        self._refresh_tree()

    def get_selected_index(self):
        if not self.is_open() or self.tree is None:
            return None
        selection = self.tree.selection()
        return self.tree.index(selection[0]) if selection else None

    def delete_selected(self, event=None):
        index = self.get_selected_index()
        if index is not None and self.on_delete_callback is not None:
            self.on_delete_callback(index)

    def _on_tree_select(self, event=None):
        if self.on_select_callback is not None:
            self.on_select_callback(self.get_selected_index())

    def _refresh_tree(self):
        if not self.is_open() or self.tree is None:
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, (name, x1, y1, x2, y2) in enumerate(self._rows, start=1):
            self.tree.insert("", tk.END, values=(idx, name, x1, y1, x2, y2))