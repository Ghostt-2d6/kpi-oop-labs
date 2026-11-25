import tkinter as tk
from tkinter import messagebox
from my_editor import MyEditor
from toolbar import Toolbar


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1040x680")
        self.root.minsize(820, 520)
        self.shape_var = tk.IntVar(value=Toolbar.ID_POINT)
        self._create_menu()
        self.toolbar = Toolbar(self.root, self.on_toolbar_command)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas = tk.Canvas(self.root, bg="white", cursor="crosshair")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.status_label = tk.Label(
            self.root, text="", bd=1, relief=tk.SUNKEN,
            anchor=tk.W, padx=8, pady=3, font=("Segoe UI", 9)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor = MyEditor.create(self.canvas)
        self.cursor_pos = (0, 0)
        self._bind_events()
        self.select_shape_tool(Toolbar.ID_POINT)

    def _create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Скасувати останній", command=self.on_file_undo)
        file_menu.add_command(label="Очистити", command=self.on_file_clear)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.on_file_exit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        objects_menu = tk.Menu(menubar, tearoff=0)
        objects_menu.add_radiobutton(
            label="Крапка", variable=self.shape_var, value=Toolbar.ID_POINT,
            command=lambda: self.select_shape_tool(Toolbar.ID_POINT)
        )
        objects_menu.add_radiobutton(
            label="Лінія", variable=self.shape_var, value=Toolbar.ID_LINE,
            command=lambda: self.select_shape_tool(Toolbar.ID_LINE)
        )
        objects_menu.add_radiobutton(
            label="Прямокутник", variable=self.shape_var, value=Toolbar.ID_RECT,
            command=lambda: self.select_shape_tool(Toolbar.ID_RECT)
        )
        objects_menu.add_radiobutton(
            label="Еліпс", variable=self.shape_var, value=Toolbar.ID_ELLIPSE,
            command=lambda: self.select_shape_tool(Toolbar.ID_ELLIPSE)
        )
        objects_menu.add_radiobutton(
            label="Лінія з кружечками", variable=self.shape_var, value=Toolbar.ID_LINE_OO,
            command=lambda: self.select_shape_tool(Toolbar.ID_LINE_OO)
        )
        objects_menu.add_radiobutton(
            label="Каркас куба", variable=self.shape_var, value=Toolbar.ID_CUBE,
            command=lambda: self.select_shape_tool(Toolbar.ID_CUBE)
        )
        menubar.add_cascade(label="Об’єкти", menu=objects_menu)

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
        else:
            self.select_shape_tool(control_id)

    def select_shape_tool(self, tool_id):
        if self.editor is None:
            return
        self.shape_var.set(tool_id)
        self.toolbar.set_active_button(tool_id)
        if tool_id == Toolbar.ID_POINT:
            self.editor.start_point_editor()
        elif tool_id == Toolbar.ID_LINE:
            self.editor.start_line_editor()
        elif tool_id == Toolbar.ID_RECT:
            self.editor.start_rect_editor()
        elif tool_id == Toolbar.ID_ELLIPSE:
            self.editor.start_ellipse_editor()
        elif tool_id == Toolbar.ID_LINE_OO:
            self.editor.start_line_oo_editor()
        elif tool_id == Toolbar.ID_CUBE:
            self.editor.start_cube_editor()
        self.update_window_title()
        self.update_status_bar()

    def update_window_title(self):
        if self.editor is None:
            return
        current_shape = self.editor.get_current_type()
        self.root.title(f"Lab4 — {current_shape}")

    def update_status_bar(self):
        if self.editor is None:
            return
        shape_name = self.editor.get_current_type()
        count = self.editor.get_count()
        capacity = self.editor.get_capacity()
        x, y = self.cursor_pos
        state = "динамічний" if self.editor.is_alive else "знищено"
        self.status_label.config(
            text=(
                f"Об’єкт: {shape_name}   |   Координати: ({x}, {y})   |   "
                f"Збережено фігур: {count} / {capacity}   |   MyEditor: {state}"
            )
        )

    def on_cursor_track(self, event):
        self.cursor_pos = (event.x, event.y)
        self.update_status_bar()

    def on_lbutton_down(self, event):
        if self.editor is None:
            return
        self.cursor_pos = (event.x, event.y)
        self.editor.on_lb_down(event.x, event.y)
        self.update_status_bar()

    def on_mouse_move(self, event):
        if self.editor is None:
            return
        self.cursor_pos = (event.x, event.y)
        self.editor.on_mouse_move(event.x, event.y)
        self.update_status_bar()

    def on_lbutton_up(self, event):
        if self.editor is None:
            return
        self.cursor_pos = (event.x, event.y)
        self.editor.on_lb_up(event.x, event.y)
        self.update_status_bar()

    def on_paint(self, event=None):
        if self.editor is not None:
            self.editor.on_paint()

    def on_file_undo(self):
        if self.editor is not None:
            self.editor.undo_last()
            self.update_status_bar()

    def on_file_clear(self):
        if self.editor is not None:
            self.editor.clear_all()
            self.update_status_bar()

    def _destroy_editor(self):
        if self.editor is not None:
            self.editor.destroy()
            self.editor = None

    def on_file_exit(self):
        self._destroy_editor()
        self.root.destroy()

    def on_help_about(self):
        messagebox.showinfo(
            "Про програму",
            "Графічний редактор Lab4\nВаріант № 8 (динамічний об’єкт MyEditor, N = 109)\nВиконав: Зазуля Віктор Іванович, ІМ-55"
        )

    def run(self):
        self.root.mainloop()