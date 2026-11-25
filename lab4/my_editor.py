from shape import (
    Shape, PointShape, LineShape, RectShape,
    EllipseShape, LineOOShape, CubeShape
)


class MyEditor:
    VARIANT_NUMBER = 8
    MAX_SHAPES = 109
    _active_instances = 0

    def __init__(self, canvas):
        self.canvas = canvas
        self.pcshape: list[Shape | None] | None = self._create_storage()
        self.shape_count = 0
        self.current_shape_cls = None
        self.preview_shape = None
        self.current_type = ""
        self.is_drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.rubber_ids = []
        self.is_alive = True
        MyEditor._active_instances += 1
        self.start_point_editor()

    def _create_storage(self) -> list[Shape | None]:
        storage: list[Shape | None] = []
        storage.extend([None] * self.MAX_SHAPES)
        return storage

    @classmethod
    def create(cls, canvas):
        return cls(canvas)

    def destroy(self):
        if not self.is_alive:
            return
        self.clear_rubber_band()
        if self.pcshape is not None:
            for i in range(self.MAX_SHAPES):
                self.pcshape[i] = None
            self.pcshape = None
        self.shape_count = 0
        self.current_shape_cls = None
        self.preview_shape = None
        self.canvas = None
        self.is_alive = False
        if MyEditor._active_instances > 0:
            MyEditor._active_instances -= 1

    def __del__(self):
        self.destroy()

    @classmethod
    def get_active_instances(cls):
        return cls._active_instances

    def start(self, shape_cls, shape_name):
        if not self.is_alive:
            return
        self.clear_rubber_band()
        self.is_drawing = False
        self.current_shape_cls = shape_cls
        self.preview_shape = shape_cls()
        self.current_type = shape_name

    def start_point_editor(self):
        self.start(PointShape, "Крапка")

    def start_line_editor(self):
        self.start(LineShape, "Лінія")

    def start_rect_editor(self):
        self.start(RectShape, "Прямокутник")

    def start_ellipse_editor(self):
        self.start(EllipseShape, "Еліпс")

    def start_line_oo_editor(self):
        self.start(LineOOShape, "Лінія з кружечками")

    def start_cube_editor(self):
        self.start(CubeShape, "Каркас куба")

    def get_current_type(self):
        return self.current_type

    def get_count(self):
        return self.shape_count

    def get_capacity(self):
        return self.MAX_SHAPES

    def add_shape(self, shape):
        if not self.is_alive or self.pcshape is None:
            return False
        if self.shape_count < self.MAX_SHAPES:
            self.pcshape[self.shape_count] = shape
            self.shape_count += 1
            return True
        return False

    def undo_last(self):
        if not self.is_alive or self.pcshape is None:
            return False
        if self.shape_count > 0:
            self.shape_count -= 1
            self.pcshape[self.shape_count] = None
            self.on_paint()
            return True
        return False

    def clear_all(self):
        if not self.is_alive:
            return
        self.clear_rubber_band()
        self.pcshape = self._create_storage()
        self.shape_count = 0
        if self.canvas is not None:
            self.canvas.delete("all")

    def clear_rubber_band(self):
        if self.canvas is not None:
            for item_id in self.rubber_ids:
                self.canvas.delete(item_id)
        self.rubber_ids.clear()

    def on_lb_down(self, x, y):
        if not self.is_alive:
            return
        self.is_drawing = True
        self.start_x = x
        self.start_y = y
        self.current_x = x
        self.current_y = y

    def on_mouse_move(self, x, y):
        if not self.is_alive or not self.is_drawing or self.preview_shape is None:
            return
        self.current_x = x
        self.current_y = y
        self.clear_rubber_band()
        self.preview_shape.set_coords(
            self.start_x, self.start_y, self.current_x, self.current_y
        )
        self.rubber_ids = self.preview_shape.show_rubber_band(self.canvas)

    def on_lb_up(self, x, y):
        if not self.is_alive or not self.is_drawing:
            return
        self.current_x = x
        self.current_y = y
        self.is_drawing = False
        self.clear_rubber_band()
        if self.current_shape_cls is not None:
            shape = self.current_shape_cls(
                self.start_x, self.start_y, self.current_x, self.current_y
            )
            self.add_shape(shape)
        self.on_paint()

    def on_paint(self):
        if not self.is_alive or self.canvas is None or self.pcshape is None:
            return
        self.canvas.delete("all")
        for i in range(self.shape_count):
            shape = self.pcshape[i]
            if shape is not None:
                shape.show(self.canvas)