from enum import Enum
import math
import tkinter as tk
from tkinter import ttk

from ipc_protocol import IpcConfig, Win32Bridge, Win32Clipboard


class Object3State(Enum):
    IDLE = "Очікування команди від Lab6"
    READING_CLIPBOARD = "Зчитування даних із Clipboard Windows"
    DRAWING = "Побудова графіка y = f(x)"
    READY = "Графік успішно побудовано"
    ERROR = "Помилка зчитування даних"


class PointParser:
    @staticmethod
    def parse(raw_text):
        if not raw_text:
            return []
        points = []
        for line in raw_text.splitlines():
            parts = line.strip().replace(",", " ").replace(";", " ").split()
            if len(parts) >= 2:
                try:
                    points.append((int(parts[0]), int(parts[1])))
                except ValueError:
                    continue
        points.sort(key=lambda pair: (pair[0], pair[1]))
        return points


class GraphCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, bg="#FFFFFF", highlightthickness=1, highlightbackground="#CCCCCC", **kwargs
        )
        self.points = []
        self.bind("<Configure>", lambda _e: self.redraw())

    def set_points(self, points):
        self.points = list(points)
        self.redraw()

    @staticmethod
    def _compute_nice_step(span, target_ticks=8):
        if span <= 0:
            return 1.0
        raw = span / max(1, target_ticks)
        mag = 10 ** math.floor(math.log10(raw))
        norm = raw / mag
        nice = 1.0 if norm <= 1.0 else (2.0 if norm <= 2.0 else (5.0 if norm <= 5.0 else 10.0))
        return nice * mag

    @staticmethod
    def _generate_ticks(min_val, max_val, step):
        ticks, cur = [], math.ceil(min_val / step) * step
        limit = max_val + step * 1e-6
        while cur <= limit:
            ticks.append(0.0 if abs(cur) < step * 1e-9 else round(cur, 6))
            cur += step
        return ticks

    @staticmethod
    def _format_tick(val):
        return str(int(round(val))) if abs(val - round(val)) < 1e-6 else f"{val:.1f}"

    def redraw(self):
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width < 120 or height < 120:
            return
        if not self.points:
            self.create_text(
                width // 2, height // 2, text="Очікування даних для побудови графіка y = f(x)",
                fill="#777777", font=("Segoe UI", 11),
            )
            return

        pad_l, pad_r, pad_t, pad_b = 68, 36, 36, 52
        plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
        if plot_w <= 20 or plot_h <= 20:
            return

        xs, ys = [p[0] for p in self.points], [p[1] for p in self.points]
        x_min, x_max, y_min, y_max = min(xs), max(xs), min(ys), max(ys)
        if x_min == x_max:
            x_min, x_max = x_min - 5, x_max + 5
        if y_min == y_max:
            y_min, y_max = y_min - 5, y_max + 5

        xm, ym = (x_max - x_min) * 0.08, (y_max - y_min) * 0.10
        vx_min, vx_max, vy_min, vy_max = x_min - xm, x_max + xm, y_min - ym, y_max + ym
        to_sx = lambda v: pad_l + (v - vx_min) / (vx_max - vx_min) * plot_w
        to_sy = lambda v: pad_t + (vy_max - v) / (vy_max - vy_min) * plot_h

        x_ticks = self._generate_ticks(vx_min, vx_max, self._compute_nice_step(vx_max - vx_min, 8))
        y_ticks = self._generate_ticks(vy_min, vy_max, self._compute_nice_step(vy_max - vy_min, 8))
        for tx in x_ticks:
            sx = to_sx(tx)
            self.create_line(sx, pad_t, sx, pad_t + plot_h, fill="#EAECEE", dash=(2, 3))
        for ty in y_ticks:
            sy = to_sy(ty)
            self.create_line(pad_l, sy, pad_l + plot_w, sy, fill="#EAECEE", dash=(2, 3))

        self.create_rectangle(pad_l, pad_t, pad_l + plot_w, pad_t + plot_h, outline="#BFC9CA")
        x_axis_y = to_sy(0.0) if vy_min <= 0.0 <= vy_max else pad_t + plot_h
        y_axis_x = to_sx(0.0) if vx_min <= 0.0 <= vx_max else pad_l

        self.create_line(pad_l, x_axis_y, pad_l + plot_w + 14, x_axis_y, fill="#1C2833", width=2, arrow=tk.LAST)
        self.create_line(y_axis_x, pad_t + plot_h, y_axis_x, pad_t - 14, fill="#1C2833", width=2, arrow=tk.LAST)
        self.create_text(pad_l + plot_w + 18, x_axis_y, text="X", anchor=tk.W, font=("Segoe UI", 10, "bold"))
        self.create_text(y_axis_x, pad_t - 22, text="Y", anchor=tk.S, font=("Segoe UI", 10, "bold"))

        lbl_y = min(pad_t + plot_h + 16, x_axis_y + 16)
        for tx in x_ticks:
            sx = to_sx(tx)
            self.create_line(sx, x_axis_y - 4, sx, x_axis_y + 4, fill="#1C2833")
            if abs(sx - y_axis_x) > 14 or abs(x_axis_y - (pad_t + plot_h)) < 2:
                self.create_text(sx, lbl_y, text=self._format_tick(tx), font=("Segoe UI", 8), fill="#2C3E50")

        lbl_x = max(pad_l - 8, y_axis_x - 8)
        for ty in y_ticks:
            sy = to_sy(ty)
            self.create_line(y_axis_x - 4, sy, y_axis_x + 4, sy, fill="#1C2833")
            if abs(sy - x_axis_y) > 12 or abs(y_axis_x - pad_l) < 2:
                self.create_text(lbl_x, sy, text=self._format_tick(ty), anchor=tk.E, font=("Segoe UI", 8), fill="#2C3E50")

        coords, screen_pts = [], []
        for x_val, y_val in self.points:
            sx, sy = to_sx(x_val), to_sy(y_val)
            coords.extend([sx, sy])
            screen_pts.append((sx, sy, x_val, y_val))
        if len(coords) >= 4:
            self.create_line(*coords, fill="#1F618D", width=2.2)

        r = 4 if len(screen_pts) <= 60 else 2.5
        show_lbl = len(screen_pts) <= 18
        for sx, sy, x_val, y_val in screen_pts:
            self.create_oval(sx - r, sy - r, sx + r, sy + r, fill="#C0392B", outline="#FFFFFF")
            if show_lbl:
                self.create_text(sx + 6, sy - 10, text=f"({x_val}; {y_val})", anchor=tk.W, font=("Segoe UI", 8))


class Object3Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Object3_Init")
        self.root.geometry("680x640+820+20")
        self.root.minsize(420, 380)
        self.bridge = Win32Bridge()
        self.clipboard = Win32Clipboard()
        self.state = Object3State.IDLE
        self.hwnd_self = 0
        self.old_wndproc = None
        self.wndproc_ref = None
        self._closing = False
        self.state_var = tk.StringVar(value=self.state.value)
        self.info_var = tk.StringVar(value="Точок на графіку: 0")
        self._build_ui()
        self._install_message_hook()
        self.root.title(IpcConfig.OBJECT3_TITLE)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        box = ttk.Frame(self.root, padding=10)
        box.pack(fill=tk.BOTH, expand=True)
        hdr = ttk.Frame(box)
        hdr.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(hdr, text="Object3 — Графік функції y = f(x)", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        ttk.Label(hdr, textvariable=self.info_var, font=("Segoe UI", 9)).pack(side=tk.RIGHT)
        ttk.Label(box, textvariable=self.state_var, foreground="#1F618D", font=("Segoe UI", 9, "bold")).pack(
            anchor=tk.W, pady=(0, 6)
        )
        self.canvas = GraphCanvas(box)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _install_message_hook(self):
        self.hwnd_self = self.bridge.get_toplevel_hwnd(self.root)
        self.old_wndproc, self.wndproc_ref = self.bridge.hook_window(self.hwnd_self, self._wnd_proc)

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == IpcConfig.WM_OBJ3_DRAW:
            self.root.after(10, lambda s=int(wparam): self._process_clipboard(s))
            return 1
        if msg == IpcConfig.WM_CLOSE:
            self.root.after(0, self._on_close)
            return 0
        return self.bridge.call_default_proc(self.old_wndproc, hwnd, msg, wparam, lparam)

    def _set_state(self, new_state):
        self.state = new_state
        self.state_var.set(new_state.value)

    def _process_clipboard(self, sender_hwnd):
        self._set_state(Object3State.READING_CLIPBOARD)
        points = PointParser.parse(self.clipboard.read_text())
        if not points:
            self._set_state(Object3State.ERROR)
            self.info_var.set("Помилка: буфер обміну порожній або має невірний формат")
            if sender_hwnd:
                self.bridge.post_message(sender_hwnd, IpcConfig.WM_OBJ_ERROR, self.hwnd_self, 301)
            return
        self._set_state(Object3State.DRAWING)
        self.canvas.set_points(points)
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        self.info_var.set(f"Точок: {len(points)} | X: [{min(xs)}; {max(xs)}] | Y: [{min(ys)}; {max(ys)}]")
        self._set_state(Object3State.READY)
        self.root.update_idletasks()
        if sender_hwnd:
            self.bridge.post_message(sender_hwnd, IpcConfig.WM_OBJ3_READY, self.hwnd_self, len(points))

    def _on_close(self):
        if self._closing:
            return
        self._closing = True
        self.bridge.unhook_window(self.hwnd_self, self.old_wndproc)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Object3Application().run()