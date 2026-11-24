"""
Модуль module2.py - реалізація діалогового вікна для пункту меню 'Робота2'.
Варіант В2 = (8 + 1) mod 4 = 1:
Вікно діалогу з горизонтальним повзунком (діапазон 1..100) та кнопками [Так] і [Відміна].
"""

import tkinter as tk
from typing import Callable

# Назовні експортується лише функція запуску діалогу
__all__ = ["open_dialog"]


class _NumberScrollDialog:
    """Інкапсульоване діалогове вікно вибору числа повзунком (ресурси та callback-функції приватні)."""

    def __init__(self, parent: tk.Misc, on_confirm: Callable[[int], None]) -> None:
        self._on_confirm = on_confirm

        self._window = tk.Toplevel(parent)
        self._window.title("Робота2 - Вибір числа (1..100)")
        self._window.geometry("380x175")
        self._window.resizable(False, False)
        self._window.transient(parent)

        self._build_ui()

    def _build_ui(self) -> None:
        """Створення елементів інтерфейсу (ресурсів) діалогового вікна."""
        frame = tk.Frame(self._window, padx=16, pady=14)
        frame.pack(fill=tk.BOTH, expand=True)

        self._value_var = tk.IntVar(value=50)
        self._status_label = tk.Label(
            frame,
            text="Вибране число: 50",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self._status_label.pack(fill=tk.X, pady=(0, 8))

        # Горизонтальний повзунок у діапазоні від 1 до 100
        self._scale = tk.Scale(
            frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self._value_var,
            showvalue=False,
            length=340,
            command=self._on_scroll_change,
        )
        self._scale.pack(fill=tk.X, pady=(0, 14))
        self._scale.focus_set()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="Так",
            width=12,
            command=self._on_ok,
        ).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(
            btn_frame,
            text="Відміна",
            width=12,
            command=self._on_cancel,
        ).pack(side=tk.RIGHT)

        self._window.bind("<Return>", lambda _event: self._on_ok())
        self._window.bind("<Escape>", lambda _event: self._on_cancel())
        self._window.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_scroll_change(self, value: str) -> None:
        """Приватна callback-функція оновлення мітки під час руху повзунка."""
        self._status_label.config(text=f"Вибране число: {int(float(value))}")

    def _on_ok(self) -> None:
        """Приватна callback-функція кнопки [Так]."""
        selected_value = int(self._value_var.get())
        self._on_confirm(selected_value)
        self._window.destroy()

    def _on_cancel(self) -> None:
        """Приватна callback-функція кнопки [Відміна]."""
        self._window.destroy()

    @property
    def window(self) -> tk.Toplevel:
        return self._window


def open_dialog(parent: tk.Misc, on_confirm: Callable[[int], None]) -> tk.Toplevel:
    """Публічна точка входу модуля для створення та відображення діалогового вікна."""
    dialog = _NumberScrollDialog(parent, on_confirm)
    return dialog.window