import tkinter as tk


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)

    def on_enter(self, event=None):
        if self.tip_window is not None or not self.text:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tip_window, text=self.text, background="#FFFFE0",
            foreground="#000000", relief=tk.SOLID, borderwidth=1,
            font=("Segoe UI", 9), padx=6, pady=2
        )
        label.pack()

    def on_leave(self, event=None):
        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None


class Toolbar(tk.Frame):
    ID_POINT = 101
    ID_LINE = 102
    ID_RECT = 103
    ID_ELLIPSE = 104
    ID_LINE_OO = 105
    ID_CUBE = 106
    ID_CLEAR = 107
    TTN_NEEDTEXT = 1
    BN_CLICKED = 0

    def __init__(self, master, command_callback):
        super().__init__(master, bd=1, relief=tk.RAISED, bg="#F0F0F0")
        self.command_callback = command_callback
        self.buttons = {}
        self.tooltips = {}
        self.active_id = None
        self._create_buttons()

    def _create_buttons(self):
        shape_items = [
            (self.ID_POINT, "• Крапка", "Крапка"),
            (self.ID_LINE, "╱ Лінія", "Лінія"),
            (self.ID_RECT, "▭ Прямокутник", "Прямокутник"),
            (self.ID_ELLIPSE, "◯ Еліпс", "Еліпс"),
            (self.ID_LINE_OO, "o—o Лінія з кружечками", "Лінія з кружечками"),
            (self.ID_CUBE, "❐ Каркас куба", "Каркас куба")
        ]
        for tool_id, label_text, tip_text in shape_items:
            btn = tk.Button(
                self, text=label_text, relief=tk.FLAT, bg="#F0F0F0",
                activebackground="#D0E4F5", padx=8, pady=4, font=("Segoe UI", 9),
                command=lambda tid=tool_id: self.on_notify(tid, self.BN_CLICKED)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.buttons[tool_id] = btn
            self.tooltips[tool_id] = ToolTip(btn, tip_text)

        separator = tk.Frame(self, width=2, bd=1, relief=tk.SUNKEN, bg="#CCCCCC")
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

        clear_btn = tk.Button(
            self, text="✕ Очистити", relief=tk.FLAT, bg="#F0F0F0",
            activebackground="#F5D0D0", padx=8, pady=4, font=("Segoe UI", 9),
            command=lambda: self.on_notify(self.ID_CLEAR, self.BN_CLICKED)
        )
        clear_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.tooltips[self.ID_CLEAR] = ToolTip(clear_btn, "Очистити полотно")

    def on_notify(self, control_id, code):
        if code == self.TTN_NEEDTEXT:
            tip = self.tooltips.get(control_id)
            return tip.text if tip is not None else ""
        if code == self.BN_CLICKED:
            if control_id in self.buttons:
                self.set_active_button(control_id)
            if self.command_callback is not None:
                self.command_callback(control_id)
        return None

    def set_active_button(self, control_id):
        self.active_id = control_id
        for tid, btn in self.buttons.items():
            if tid == control_id:
                btn.config(relief=tk.SUNKEN, bg="#CCE4F7")
            else:
                btn.config(relief=tk.FLAT, bg="#F0F0F0")