"""
Головний модуль проєкту Lab1.
Лабораторна робота №1 (Варіант В1 = 0, В2 = 1; номер у списку Ж = 8).
"""

import tkinter as tk
import module1
import module2


class MainApplication:
    """Головне вікно програми з пунктами меню 'Робота1' та 'Робота2'."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("Lab1 - Зазуля Віктор (ІМ-55)")
        self._root.geometry("520x300")
        self._root.resizable(False, False)

        # Посилання на поточне активне діалогове вікно (для автоматичного закриття)
        self._active_dialog: tk.Toplevel | None = None

        self._create_menu()
        self._create_widgets()

    def _create_menu(self) -> None:
        """Створення головного меню програми з пунктами 'Робота1' та 'Робота2'."""
        menubar = tk.Menu(self._root)
        menubar.add_command(label="Робота1", command=self._open_work1)
        menubar.add_command(label="Робота2", command=self._open_work2)
        self._root.config(menu=menubar)

    def _create_widgets(self) -> None:
        """Створення елементів відображення результатів у головному вікні."""
        container = tk.Frame(self._root, padx=24, pady=24)
        container.pack(fill=tk.BOTH, expand=True)

        header = tk.Label(
            container,
            text="Результати роботи діалогових вікон:",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        header.pack(fill=tk.X, pady=(0, 16))

        # Блок відображення результату Робота1 (В1 = 0: введений текст)
        frame1 = tk.LabelFrame(
            container,
            text="Робота1 (Варіант 0 - введений текст)",
            font=("Segoe UI", 10),
            padx=12,
            pady=10,
        )
        frame1.pack(fill=tk.X, pady=(0, 12))

        self._text_result_var = tk.StringVar(value="- текст ще не введено -")
        tk.Label(
            frame1,
            textvariable=self._text_result_var,
            font=("Segoe UI", 11),
            fg="#1a365d",
            anchor="w",
        ).pack(fill=tk.X)

        # Блок відображення результату Робота2 (В2 = 1: вибране число 1..100)
        frame2 = tk.LabelFrame(
            container,
            text="Робота2 (Варіант 1 - вибране число)",
            font=("Segoe UI", 10),
            padx=12,
            pady=10,
        )
        frame2.pack(fill=tk.X)

        self._number_result_var = tk.StringVar(value="- число ще не вибрано -")
        tk.Label(
            frame2,
            textvariable=self._number_result_var,
            font=("Segoe UI", 11),
            fg="#1a365d",
            anchor="w",
        ).pack(fill=tk.X)

    def _close_previous_dialog(self) -> None:
        """Автоматично закриває попереднє діалогове вікно, якщо воно відкрите."""
        if self._active_dialog is not None and self._active_dialog.winfo_exists():
            self._active_dialog.destroy()
        self._active_dialog = None

    def _on_work1_confirm(self, entered_text: str) -> None:
        """Оновлює текст у головному вікні після підтвердження в Робота1."""
        self._text_result_var.set(entered_text)

    def _on_work2_confirm(self, selected_number: int) -> None:
        """Оновлює число у головному вікні після підтвердження в Робота2."""
        self._number_result_var.set(str(selected_number))

    def _open_work1(self) -> None:
        """Обробник вибору пункту меню 'Робота1'."""
        self._close_previous_dialog()
        self._active_dialog = module1.open_dialog(self._root, self._on_work1_confirm)

    def _open_work2(self) -> None:
        """Обробник вибору пункту меню 'Робота2'."""
        self._close_previous_dialog()
        self._active_dialog = module2.open_dialog(self._root, self._on_work2_confirm)


def main() -> None:
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()