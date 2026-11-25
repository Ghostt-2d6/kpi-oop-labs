import tkinter as tk
from tkinter import filedialog, messagebox
from my_editor import MyEditor
from my_table import MyTable
from toolbar import Toolbar


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1080x680")
        self.root.minsize(860, 520)
        self.shape_var = tk.IntVar(value=Toolbar.ID_POINT)
        self.table_open_var = tk.BooleanVar(value=False)
        self._create_menu()
        self.toolbar = Toolbar(self.root, self.on_toolbar_command)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas = tk.Canvas(self.root, bg="white", cursor="crosshair")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.status_label = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=8, pady=3, font=("Segoe UI", 9))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor = MyEditor.get_instance(self.canvas)
        self.table = MyTable(self.root, on_select_callback=self.on_table_select, on_delete_callback=self.on_table_delete, on_close_callback=self.on_table_closed)
        self.cursor_pos = (0, 0)
        self._bind_events()
        self.select_shape_tool(Toolbar.ID_POINT)

    def _create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Зберегти у файл...", command=self.on_file_save)
        file_menu.add_command(label="Завантажити з файлу...", command=self.on_file_load)
        file_menu.add_separator()
        file_menu.add_command(label="Скасувати останній", command=self.on_file_undo)
        file_menu.add_command(label="Очистити", command=self.on_file_clear)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.on_file_exit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        objects_menu = tk.Menu(menubar, tearoff=0)
        for label, tid in [
            ("Крапка", Toolbar.ID_POINT),
            ("Лінія", Toolbar.ID_LINE),
            ("Прямокутник", Toolbar.ID_RECT),
            ("Еліпс", Toolbar.ID_ELLIPSE),
            ("Лінія з кружечками", Toolbar.ID_LINE_OO),
            ("Каркас куба", Toolbar.ID_CUBE)
        ]:
            objects_menu.add_radiobutton(label=label, variable=self.shape_var, value=tid, command=lambda t=tid: self.select_shape_tool(t))
        menubar.add_cascade(label="Об’єкти", menu=objects_menu)

        table_menu = tk.Menu(menubar, tearoff=0)
        table_menu.add_checkbutton(label="Вікно таблиці", variable=self.table_open_var, command=self.on_toggle_table)
        menubar.add_cascade(label="Таблиця", menu=table_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Про програму", command=self.on_help_about)
        menubar.add_cascade(label="Довідка", menu=help_menu)

        self.root.config(menu=menubar)

    def _bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_lbutton_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<Motion>", self.on_cursor_track)
        self.canvas.bind("<ButtonRelease-1>", self.on_lbutton_up)
        self.canvas.bind("<Configure>", self.on_paint)
        self.root.protocol("WM_DELETE_WINDOW", self.on_file_exit)

    def on_toolbar_command(self, control_id):
        if control_id == Toolbar.ID_CLEAR:
            self.on_file_clear()
        elif control_id == Toolbar.ID_TABLE:
            self.on_toggle_table()
        else:
            self.select_shape_tool(control_id)

    def on_toggle_table(self):
        self.table.toggle_window()
        is_open = self.table.is_open()
        self.table_open_var.set(is_open)
        self.toolbar.set_table_active(is_open)

    def on_table_closed(self):
        self.table_open_var.set(False)
        self.toolbar.set_table_active(False)

    def on_table_select(self, index):
        if self.editor is not None:
            self.editor.set_selected_index(index)
            self.update_status_bar()

    def on_table_delete(self, index):
        if self.editor is not None and self.editor.remove_shape_at(index):
            self.table.set_rows(self.editor.get_table_rows())
            self.update_status_bar()

    def select_shape_tool(self, tool_id):
        if self.editor is None:
            return
        self.shape_var.set(tool_id)
        self.toolbar.set_active_button(tool_id)
        handlers = {
            Toolbar.ID_POINT: self.editor.start_point_editor,
            Toolbar.ID_LINE: self.editor.start_line_editor,
            Toolbar.ID_RECT: self.editor.start_rect_editor,
            Toolbar.ID_ELLIPSE: self.editor.start_ellipse_editor,
            Toolbar.ID_LINE_OO: self.editor.start_line_oo_editor,
            Toolbar.ID_CUBE: self.editor.start_cube_editor
        }
        handler = handlers.get(tool_id)
        if handler is not None:
            handler()
        self.update_window_title()
        self.update_status_bar()

    def update_window_title(self):
        if self.editor is not None:
            self.root.title(f"Lab5 — {self.editor.get_current_type()}")

    def update_status_bar(self):
        if self.editor is None:
            return
        shape_name = self.editor.get_current_type()
        count, capacity = self.editor.get_count(), self.editor.get_capacity()
        x, y = self.cursor_pos
        state = "Singleton (активний)" if self.editor.is_alive else "знищено"
        self.status_label.config(text=f"Об’єкт: {shape_name}   |   Координати: ({x}, {y})   |   Збережено фігур: {count} / {capacity}   |   MyEditor: {state}")

    def on_cursor_track(self, event):
        self.cursor_pos = (event.x, event.y)
        self.update_status_bar()

    def on_lbutton_down(self, event):
        if self.editor is not None:
            self.cursor_pos = (event.x, event.y)
            self.editor.on_lb_down(event.x, event.y)
            self.update_status_bar()

    def on_mouse_move(self, event):
        if self.editor is not None:
            self.cursor_pos = (event.x, event.y)
            self.editor.on_mouse_move(event.x, event.y)
            self.update_status_bar()

    def on_lbutton_up(self, event):
        if self.editor is None:
            return
        self.cursor_pos = (event.x, event.y)
        created = self.editor.on_lb_up(event.x, event.y)
        if created is not None:
            x1, y1, x2, y2 = created.get_coords()
            self.table.add_row(created.get_display_name(), x1, y1, x2, y2)
        self.update_status_bar()

    def on_paint(self, event=None):
        if self.editor is not None:
            self.editor.on_paint()

    def on_file_save(self):
        if self.editor is None:
            return
        filepath = filedialog.asksaveasfilename(title="Зберегти множину об’єктів", defaultextension=".txt", initialfile="shapes.txt", filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")])
        if not filepath:
            return
        try:
            saved_count = self.editor.save_to_file(filepath)
            messagebox.showinfo("Збереження завершено", f"У файл успішно записано об’єктів: {saved_count}")
        except OSError as exc:
            messagebox.showerror("Помилка запису файлу", str(exc))

    def on_file_load(self):
        if self.editor is None:
            return
        filepath = filedialog.askopenfilename(title="Завантажити множину об’єктів", filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")])
        if not filepath:
            return
        try:
            loaded_count = self.editor.load_from_file(filepath)
            self.table.set_rows(self.editor.get_table_rows())
            self.update_status_bar()
            messagebox.showinfo("Завантаження завершено", f"Із файлу успішно завантажено об’єктів: {loaded_count}")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Помилка читання файлу", str(exc))

    def on_file_undo(self):
        if self.editor is not None and self.editor.undo_last():
            self.table.set_rows(self.editor.get_table_rows())
            self.update_status_bar()

    def on_file_clear(self):
        if self.editor is not None:
            self.editor.clear_all()
            self.table.clear_rows()
            self.update_status_bar()

    def _destroy_editor(self):
        if self.editor is not None:
            self.editor.destroy()
            self.editor = None

    def on_file_exit(self):
        self.table.close_window()
        self._destroy_editor()
        self.root.destroy()

    def on_help_about(self):
        messagebox.showinfo("Про програму", "Графічний редактор Lab5\nВаріант № 8 (класичний Singleton MyEditor, N = 109)\nВиконав: Зазуля Віктор Іванович, ІМ-55")

    def run(self):
        self.root.mainloop()
