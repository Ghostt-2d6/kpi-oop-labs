import ctypes
from enum import Enum
import random
import struct
import tkinter as tk
from tkinter import ttk

from ipc_protocol import CopyDataStruct, IpcConfig, Win32Bridge, Win32Clipboard


class Object2State(Enum):
    IDLE = "Очікування параметрів від Lab6"
    GENERATING = "Генерація пар координат (x, y)"
    WRITING_CLIPBOARD = "Запис даних у Clipboard Windows"
    READY = "Дані згенеровано та записано в Clipboard"
    ERROR = "Помилка обробки даних"


class PointGenerator:
    @staticmethod
    def generate(n_point, x_min, x_max, y_min, y_max):
        return [
            (random.randint(x_min, x_max), random.randint(y_min, y_max))
            for _ in range(n_point)
        ]

    @staticmethod
    def format_for_clipboard(points):
        return "\r\n".join(f"{x}\t{y}" for x, y in points)


class Object2Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Object2_Init")
        self.root.geometry("360x640+420+20")
        self.root.minsize(300, 380)
        self.bridge = Win32Bridge()
        self.clipboard = Win32Clipboard()
        self.state = Object2State.IDLE
        self.hwnd_self = 0
        self.old_wndproc = None
        self.wndproc_ref = None
        self._closing = False
        self.points = []
        self.state_var = tk.StringVar(value=self.state.value)
        self.info_var = tk.StringVar(value="Кількість точок: 0")
        self._build_ui()
        self._install_message_hook()
        self.root.title(IpcConfig.OBJECT2_TITLE)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        box = ttk.Frame(self.root, padding=10)
        box.pack(fill=tk.BOTH, expand=True)
        ttk.Label(box, text="Object2 — Згенеровані точки (x, y)", font=("Segoe UI", 11, "bold")).pack(
            anchor=tk.W, pady=(0, 6)
        )
        ttk.Label(box, textvariable=self.state_var, foreground="#1E8449", font=("Segoe UI", 9, "bold")).pack(
            anchor=tk.W, pady=(0, 4)
        )
        ttk.Label(box, textvariable=self.info_var).pack(anchor=tk.W, pady=(0, 8))
        tbl = ttk.Frame(box)
        tbl.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tbl, columns=("index", "x", "y"), show="headings")
        for col, title, w in (("index", "№", 55), ("x", "X", 120), ("y", "Y", 120)):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=w, anchor=tk.CENTER)
        sb = ttk.Scrollbar(tbl, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _install_message_hook(self):
        self.hwnd_self = self.bridge.get_toplevel_hwnd(self.root)
        self.old_wndproc, self.wndproc_ref = self.bridge.hook_window(self.hwnd_self, self._wnd_proc)

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == IpcConfig.WM_COPYDATA:
            cds = ctypes.cast(lparam, ctypes.POINTER(CopyDataStruct)).contents
            if cds.dwData == IpcConfig.COPYDATA_PARAMS_ID and cds.cbData == 20 and cds.lpData:
                params = struct.unpack("<5i", ctypes.string_at(cds.lpData, cds.cbData))
                self.root.after(10, lambda s=int(wparam), p=params: self._process_params(s, p))
                return 1
            return 0
        if msg == IpcConfig.WM_CLOSE:
            self.root.after(0, self._on_close)
            return 0
        return self.bridge.call_default_proc(self.old_wndproc, hwnd, msg, wparam, lparam)

    def _set_state(self, new_state):
        self.state = new_state
        self.state_var.set(new_state.value)

    def _process_params(self, sender_hwnd, params):
        n_point, x_min, x_max, y_min, y_max = params
        self._set_state(Object2State.GENERATING)
        self.points = PointGenerator.generate(n_point, x_min, x_max, y_min, y_max)
        self._render_table(n_point, x_min, x_max, y_min, y_max)
        self._set_state(Object2State.WRITING_CLIPBOARD)
        if not self.clipboard.write_text(PointGenerator.format_for_clipboard(self.points)):
            self._set_state(Object2State.ERROR)
            if sender_hwnd:
                self.bridge.post_message(sender_hwnd, IpcConfig.WM_OBJ_ERROR, self.hwnd_self, 201)
            return
        self._set_state(Object2State.READY)
        self.root.update_idletasks()
        if sender_hwnd:
            self.bridge.post_message(
                sender_hwnd, IpcConfig.WM_OBJ2_READY, self.hwnd_self, len(self.points)
            )

    def _render_table(self, n_point, x_min, x_max, y_min, y_max):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, (x_val, y_val) in enumerate(self.points, start=1):
            self.tree.insert("", tk.END, values=(idx, x_val, y_val))
        self.info_var.set(f"Точок: {n_point} | X: [{x_min}; {x_max}] | Y: [{y_min}; {y_max}]")

    def _on_close(self):
        if self._closing:
            return
        self._closing = True
        self.bridge.unhook_window(self.hwnd_self, self.old_wndproc)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Object2Application().run()