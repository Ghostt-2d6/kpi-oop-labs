import tkinter as tk
from tkinter import messagebox
from editor import ShapeObjectsEditor


class Lab2App:
    def __init__(self, root):
        self.root = root
        self.root.title("OOP_lab2")
        self.root.geometry("800x600")
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.editor = ShapeObjectsEditor(self.canvas)
        self.shape_vars = {
            "Крапка": tk.BooleanVar(value=False),
            "Лінія": tk.BooleanVar(value=False),
            "Прямокутник": tk.BooleanVar(value=True),
            "Еліпс": tk.BooleanVar(value=False),
        }
        self.init_menu()
        self.bind_events()

    def init_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Очистити", command=self.editor.clear_all)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.root.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

        self.objects_menu = tk.Menu(menubar, tearoff=0, postcommand=self.on_init_menu_popup)
        for name in ("Крапка", "Лінія", "Прямокутник", "Еліпс"):
            self.objects_menu.add_checkbutton(
                label=name,
                variable=self.shape_vars[name],
                command=lambda n=name: self.select_shape(n),
            )
        menubar.add_cascade(label="Об’єкти", menu=self.objects_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Про програму", command=self.show_about)
        menubar.add_cascade(label="Довідка", menu=help_menu)
        self.root.config(menu=menubar)

    def select_shape(self, shape_name):
        self.editor.set_shape_type(shape_name)
        self.on_init_menu_popup()

    def on_init_menu_popup(self):
        active = self.editor.current_type
        for name, var in self.shape_vars.items():
            var.set(name == active)

    def show_about(self):
        messagebox.showinfo(
            "Про програму",
            "Лабораторна робота №2\nГрафічний редактор об’єктів\nВиконав: Зазуля В.І., група ІМ-55 (варіант 8)",
        )

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.handle_lb_down)
        self.canvas.bind("<B1-Motion>", self.handle_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.handle_lb_up)

    def handle_lb_down(self, event):
        self.editor.on_lb_down(event.x, event.y)

    def handle_mouse_move(self, event):
        self.editor.on_mouse_move(event.x, event.y)

    def handle_lb_up(self, event):
        self.editor.on_lb_up(event.x, event.y)


def main():
    root = tk.Tk()
    app = Lab2App(root)
    root.mainloop()


if __name__ == "__main__":
    main()