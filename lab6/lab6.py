from datetime import datetime
from enum import Enum
import os
import struct
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk

from ipc_protocol import IpcConfig, Win32Bridge


class Lab6State(Enum):
    IDLE = "Очікування команди користувача"
    STARTING_OBJECT2 = "Пошук або запуск Object2"
    WAITING_OBJECT2 = "Очікування генерації даних від Object2"
    STARTING_OBJECT3 = "Пошук або запуск Object3"
    WAITING_OBJECT3 = "Очікування побудови графіка в Object3"
    COMPLETED = "Сеанс успішно завершено"
    ERROR = "Помилка виконання"


class ProcessLauncher:
    def __init__(self):
        self.spawned = []
        self.base_dir = (
            os.path.dirname(sys.executable)
            if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__))
        )

    def launch(self, name):
        exe_path = os.path.join(self.base_dir, f"{name}.exe")
        py_path = os.path.join(self.base_dir, f"{name}.py")
        if os.path.isfile(exe_path):
            self.spawned.append(subprocess.Popen([exe_path], cwd=self.base_dir))
            return True
        if os.path.isfile(py_path):
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            proc = subprocess.Popen(
                [sys.executable, py_path], cwd=self.base_dir, creationflags=flags
            )
            self.spawned.append(proc)
            return True
        return False

    def cleanup(self):
        alive = [p for p in self.spawned if p.poll() is None]
        if alive:
            time.sleep(0.15)
        for proc in alive:
            if proc.poll() is None:
                try:
                    proc.terminate()
                except OSError:
                    pass
        self.spawned.clear()


class ParamsDialog(tk.Toplevel):
    def __init__(self, parent, initial_values):
        super().__init__(parent)
        self.title("Введення параметрів (Варіант 0)")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.vars = {k: tk.StringVar(value=str(v)) for k, v in initial_values.items()}
        self._build_ui()
        self._center_on_parent(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Return>", lambda _e: self._on_confirm())
        self.bind("<Escape>", lambda _e: self._on_cancel())

    def _build_ui(self):
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(
            frame, text="Параметри генерації точок (x, y):", font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        fields = [
            ("Кількість точок (nPoint):", "nPoint"),
            ("Мінімальне значення X (xMin):", "xMin"),
            ("Максимальне значення X (xMax):", "xMax"),
            ("Мінімальне значення Y (yMin):", "yMin"),
            ("Максимальне значення Y (yMax):", "yMax"),
        ]
        for idx, (label, key) in enumerate(fields, start=1):
            ttk.Label(frame, text=label).grid(row=idx, column=0, sticky=tk.W, padx=(0, 12), pady=4)
            entry = ttk.Entry(frame, textvariable=self.vars[key], width=16)
            entry.grid(row=idx, column=1, sticky=tk.EW, pady=4)
            if idx == 1:
                entry.focus_set()
                entry.select_range(0, tk.END)
        btns = ttk.Frame(frame)
        btns.grid(row=len(fields) + 1, column=0, columnspan=2, pady=(14, 0))
        ttk.Button(btns, text="Виконати", command=self._on_confirm, width=12).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(btns, text="Відміна", command=self._on_cancel, width=12).pack(side=tk.LEFT)

    def _center_on_parent(self, parent):
        self.update_idletasks()
        x = max(20, parent.winfo_rootx() + (parent.winfo_width() - self.winfo_reqwidth()) // 2)
        y = max(20, parent.winfo_rooty() + (parent.winfo_height() - self.winfo_reqheight()) // 2)
        self.geometry(f"+{x}+{y}")

    def _on_confirm(self):
        try:
            vals = {k: int(v.get().strip()) for k, v in self.vars.items()}
        except ValueError:
            messagebox.showerror("Помилка", "Усі параметри мають бути цілими числами.", parent=self)
            return
        if not (2 <= vals["nPoint"] <= 5000):
            messagebox.showerror("Помилка", "Параметр nPoint має бути у [2; 5000].", parent=self)
            return
        if vals["xMin"] >= vals["xMax"] or vals["yMin"] >= vals["yMax"]:
            messagebox.showerror("Помилка", "Мінімальне значення має бути меншим за максимальне.", parent=self)
            return
        self.result = vals
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()


class Lab6Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lab6_Init")
        self.bridge = Win32Bridge()
        self.launcher = ProcessLauncher()
        self.state = Lab6State.IDLE
        self.last_params = {"nPoint": 15, "xMin": -20, "xMax": 20, "yMin": -50, "yMax": 50}
        self.pending_params = None
        self.hwnd_lab6 = 0
        self.old_wndproc = None
        self.wndproc_ref = None
        self.wait_ms = 0
        self._closing = False
        self.state_var = tk.StringVar(value=self.state.value)
        self.params_var = tk.StringVar(value="Параметри ще не задані")
        self._configure_layout()
        self._build_menu()
        self._build_ui()
        self._install_message_hook()
        self.root.title(IpcConfig.LAB6_TITLE)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._log("Програму Lab6 запущено. Оберіть «Робота -> Задати параметри...».")

    def _compute_screen_regions(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        m, work_h = 16, sh - 80
        w1 = max(360, int(sw * 0.28))
        w2 = max(320, int(sw * 0.24))
        w3 = max(480, sw - w1 - w2 - m * 4)
        return (m, m, w1, work_h), (m * 2 + w1, m, w2, work_h), (m * 3 + w1 + w2, m, w3, work_h)

    def _configure_layout(self):
        x, y, w, h = self._compute_screen_regions()[0]
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(340, 420)

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        work = tk.Menu(menubar, tearoff=0)
        work.add_command(label="Задати параметри...", command=self._open_params_dialog, accelerator="Ctrl+N")
        work.add_command(label="Упорядкувати вікна", command=self._arrange_all_windows)
        work.add_separator()
        work.add_command(label="Завершити Object2 та Object3", command=self._close_children)
        work.add_separator()
        work.add_command(label="Вихід", command=self._on_close)
        menubar.add_cascade(label="Робота", menu=work)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Про програму", command=self._show_about)
        menubar.add_cascade(label="Довідка", menu=help_menu)
        self.root.config(menu=menubar)
        self.root.bind("<Control-n>", lambda _e: self._open_params_dialog())

    def _build_ui(self):
        box = ttk.Frame(self.root, padding=12)
        box.pack(fill=tk.BOTH, expand=True)
        ttk.Label(box, text="Lab6 — Менеджер системи об'єктів", font=("Segoe UI", 12, "bold")).pack(
            anchor=tk.W, pady=(0, 8)
        )
        s_frame = ttk.LabelFrame(box, text="Поточний стан автомата", padding=8)
        s_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(s_frame, textvariable=self.state_var, font=("Segoe UI", 9, "bold"), foreground="#1B4F72").pack(
            anchor=tk.W
        )
        p_frame = ttk.LabelFrame(box, text="Активні параметри", padding=8)
        p_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(p_frame, textvariable=self.params_var).pack(anchor=tk.W)
        ttk.Button(box, text="Ввести параметри та виконати", command=self._open_params_dialog).pack(
            fill=tk.X, pady=(0, 8)
        )
        l_frame = ttk.LabelFrame(box, text="Журнал обміну повідомленнями", padding=6)
        l_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(
            l_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 9), bg="#FAFAFA", relief=tk.FLAT
        )
        sb = ttk.Scrollbar(l_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _install_message_hook(self):
        self.hwnd_lab6 = self.bridge.get_toplevel_hwnd(self.root)
        self.old_wndproc, self.wndproc_ref = self.bridge.hook_window(self.hwnd_lab6, self._wnd_proc)

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == IpcConfig.WM_OBJ2_READY:
            self.root.after(10, lambda c=int(lparam): self._on_object2_ready(c))
            return 1
        if msg == IpcConfig.WM_OBJ3_READY:
            self.root.after(10, lambda c=int(lparam): self._on_object3_ready(c))
            return 1
        if msg == IpcConfig.WM_OBJ_ERROR:
            self.root.after(10, lambda code=int(lparam): self._on_child_error(code))
            return 1
        return self.bridge.call_default_proc(self.old_wndproc, hwnd, msg, wparam, lparam)

    def _set_state(self, new_state):
        self.state = new_state
        self.state_var.set(new_state.value)

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _open_params_dialog(self):
        dlg = ParamsDialog(self.root, self.last_params)
        self.root.wait_window(dlg)
        if dlg.result is None:
            self._log("Введення параметрів скасовано користувачем.")
            return
        self.last_params = dlg.result
        self.pending_params = dict(dlg.result)
        p = self.pending_params
        self.params_var.set(
            f"nPoint={p['nPoint']}, X:[{p['xMin']}..{p['xMax']}], Y:[{p['yMin']}..{p['yMax']}]"
        )
        self._log(f"Початок сеансу: nPoint={p['nPoint']}, X=[{p['xMin']}; {p['xMax']}], Y=[{p['yMin']}; {p['yMax']}].")
        self._ensure_component("Object2", IpcConfig.OBJECT2_TITLE, Lab6State.STARTING_OBJECT2, self._send_to_object2)

    def _ensure_component(self, comp_name, title, wait_state, on_found):
        self._set_state(wait_state)
        hwnd = self.bridge.find_window(title)
        if hwnd:
            self._log(f"Знайдено вже запущений процес {comp_name}.")
            on_found(hwnd)
            return
        self._log(f"{comp_name} не знайдено. Автоматичний запуск {comp_name}...")
        if not self.launcher.launch(comp_name):
            self._set_state(Lab6State.ERROR)
            self._log(f"Помилка: не знайдено файл {comp_name}.exe або {comp_name}.py.")
            messagebox.showerror("Помилка запуску", f"Не вдалося знайти програму {comp_name}.")
            return
        self.wait_ms = 0
        self.root.after(
            IpcConfig.POLL_INTERVAL_MS,
            lambda: self._poll_window(comp_name, title, wait_state, on_found),
        )

    def _poll_window(self, comp_name, title, wait_state, on_found):
        if self.state != wait_state:
            return
        hwnd = self.bridge.find_window(title)
        if hwnd:
            self._log(f"Вікно {comp_name} успішно ініціалізовано.")
            self.root.after(80, lambda: on_found(hwnd))
            return
        self.wait_ms += IpcConfig.POLL_INTERVAL_MS
        if self.wait_ms >= IpcConfig.START_TIMEOUT_MS:
            self._set_state(Lab6State.ERROR)
            self._log(f"Перевищено час очікування запуску {comp_name}.")
            return
        self.root.after(
            IpcConfig.POLL_INTERVAL_MS,
            lambda: self._poll_window(comp_name, title, wait_state, on_found),
        )

    def _send_to_object2(self, hwnd_obj2):
        self.bridge.arrange_window(hwnd_obj2, *self._compute_screen_regions()[1])
        p = self.pending_params
        payload = struct.pack("<5i", p["nPoint"], p["xMin"], p["xMax"], p["yMin"], p["yMax"])
        self._set_state(Lab6State.WAITING_OBJECT2)
        self._log("Надсилання WM_COPYDATA з параметрами до Object2.")
        if not self.bridge.send_copydata(hwnd_obj2, self.hwnd_lab6, IpcConfig.COPYDATA_PARAMS_ID, payload):
            self._set_state(Lab6State.ERROR)
            self._log("Помилка доставки WM_COPYDATA до Object2.")

    def _on_object2_ready(self, count):
        self._log(f"Отримано WM_OBJ2_READY: згенеровано {count} точок і записано в Clipboard.")
        self._ensure_component("Object3", IpcConfig.OBJECT3_TITLE, Lab6State.STARTING_OBJECT3, self._notify_object3)

    def _notify_object3(self, hwnd_obj3):
        self.bridge.arrange_window(hwnd_obj3, *self._compute_screen_regions()[2])
        self._set_state(Lab6State.WAITING_OBJECT3)
        self._log("Надсилання WM_OBJ3_DRAW до Object3 для зчитування Clipboard.")
        if not self.bridge.post_message(hwnd_obj3, IpcConfig.WM_OBJ3_DRAW, self.hwnd_lab6, 0):
            self._set_state(Lab6State.ERROR)
            self._log("Помилка надсилання WM_OBJ3_DRAW до Object3.")

    def _on_object3_ready(self, count):
        self._arrange_all_windows()
        self._set_state(Lab6State.COMPLETED)
        self._log(f"Отримано WM_OBJ3_READY: побудовано графік для {count} точок.")
        self._log("Сеанс завершено. Lab6 залишається активним для повторного запуску.")
        self.root.lift()
        self.root.focus_force()

    def _on_child_error(self, code):
        self._set_state(Lab6State.ERROR)
        self._log(f"Отримано WM_OBJ_ERROR (код: {code}).")

    def _arrange_all_windows(self):
        r1, r2, r3 = self._compute_screen_regions()
        self.root.geometry(f"{r1[2]}x{r1[3]}+{r1[0]}+{r1[1]}")
        for title, rect in ((IpcConfig.OBJECT2_TITLE, r2), (IpcConfig.OBJECT3_TITLE, r3)):
            hwnd = self.bridge.find_window(title)
            if hwnd:
                self.bridge.arrange_window(hwnd, *rect)

    def _close_children(self):
        for title in (IpcConfig.OBJECT2_TITLE, IpcConfig.OBJECT3_TITLE):
            hwnd = self.bridge.find_window(title)
            if hwnd:
                self.bridge.post_message(hwnd, IpcConfig.WM_CLOSE, 0, 0)
                self._log(f"Надіслано WM_CLOSE до «{title}».")

    def _show_about(self):
        messagebox.showinfo(
            "Про програму Lab6",
            "Лабораторна робота №6 (Варіант 0)\n"
            "Lab6 (менеджер), Object2 (генератор), Object3 (графік y=f(x)).",
            parent=self.root,
        )

    def _on_close(self):
        if self._closing:
            return
        self._closing = True
        self._close_children()
        self.bridge.unhook_window(self.hwnd_lab6, self.old_wndproc)
        self.launcher.cleanup()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Lab6Application().run()