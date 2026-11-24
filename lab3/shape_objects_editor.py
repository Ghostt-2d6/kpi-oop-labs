from editor import ShapeEditor, PointEditor, LineEditor, RectEditor, EllipseEditor


class ShapeObjectsEditor:
    def __init__(self, canvas):
        self.canvas = canvas
        self.pcshape = [None] * ShapeEditor.MAX_SHAPES
        self.shape_count = 0
        self.current_editor = None
        self.current_type = ""
        self.start_point_editor()

    def _switch_editor(self, editor_cls, shape_name):
        if self.current_editor is not None:
            self.pcshape, self.shape_count = self.current_editor.get_storage()
        self.current_editor = editor_cls(self.canvas, self.pcshape, self.shape_count)
        self.current_type = shape_name

    def start_point_editor(self):
        self._switch_editor(PointEditor, "Крапка")

    def start_line_editor(self):
        self._switch_editor(LineEditor, "Лінія")

    def start_rect_editor(self):
        self._switch_editor(RectEditor, "Прямокутник")

    def start_ellipse_editor(self):
        self._switch_editor(EllipseEditor, "Еліпс")

    def get_current_type(self):
        return self.current_type

    def get_count(self):
        return self.shape_count

    def get_capacity(self):
        return ShapeEditor.MAX_SHAPES

    def on_lb_down(self, x, y):
        if self.current_editor is not None:
            self.current_editor.on_lb_down(x, y)

    def on_lb_up(self, x, y):
        if self.current_editor is not None:
            self.current_editor.on_lb_up(x, y)
            self.pcshape, self.shape_count = self.current_editor.get_storage()

    def on_mouse_move(self, x, y):
        if self.current_editor is not None:
            self.current_editor.on_mouse_move(x, y)

    def on_paint(self):
        if self.current_editor is not None:
            self.current_editor.on_paint()

    def undo_last(self):
        if self.current_editor is not None:
            result = self.current_editor.undo_last()
            self.pcshape, self.shape_count = self.current_editor.get_storage()
            return result
        return False

    def clear_all(self):
        self.pcshape = [None] * ShapeEditor.MAX_SHAPES
        self.shape_count = 0
        if self.current_editor is not None:
            self.current_editor.set_storage(self.pcshape, self.shape_count)
        self.canvas.delete("all")