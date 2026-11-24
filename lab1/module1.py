"""
Модуль module1.py - реалізація діалогового вікна для пункту меню 'Робота1'.
Варіант В1 = 8 mod 4 = 0:
Вікно діалогу для вводу тексту зі стрічкою вводу та кнопками [Так] і [Відміна].
"""

import tkinter as tk
from typing import Callable

# Назовні експортується лише функція запуску діалогу
__all__ = ["open_dialog"]


class _TextInputDialog:
    """Інкапсульоване діалогове вікно введення тексту (ресурси та callback-функції приватні)."""

    def __init__(self, parent: tk.Misc, on_confirm: Callable[[str], None]) -> None:
        self._on_confirm = on_confirm

        self._window = tk.Toplevel(parent)
        self._window.title("Робота1 - Введення тексту")
        self._window.geometry("360x150")
        self._window.resizable(False, False)
        self._window.transient(parent)

        self._build_ui()

    def _build_ui(self) -> None:
        """Створення елементів інтерфейсу (ресурсів) діалогового вікна."""
        frame = tk.Frame(self._window, padx=16, pady=14)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="Введіть рядок тексту:",
            font=("Segoe UI", 10),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 6))

        self._entry_var = tk.StringVar()
        self._entry = tk.Entry(frame, textvariable=self._entry_var, font=("Segoe UI", 10))
        self._entry.pack(fill=tk.X, pady=(0, 14))
        self._entry.focus_set()

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

    def _on_ok(self) -> None:
        """Приватна callback-функція кнопки [Так]."""
        text = self._entry_var.get()
        self._on_confirm(text)
        self._window.destroy()

    def _on_cancel(self) -> None:
        """Приватна callback-функція кнопки [Відміна]."""
        self._window.destroy()

    @property
    def window(self) -> tk.Toplevel:
        return self._window


def open_dialog(parent: tk.Misc, on_confirm: Callable[[str], None]) -> tk.Toplevel:
    """Публічна точка входу модуля для створення та відображення діалогового вікна."""
    dialog = _TextInputDialog(parent, on_confirm)
    return dialog.window