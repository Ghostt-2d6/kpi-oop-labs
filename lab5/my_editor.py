from shape import (
    Shape, PointShape, LineShape, RectShape,
    EllipseShape, LineOOShape, CubeShape
)


class MyEditor:
    VARIANT_NUMBER = 8
    MAX_SHAPES = 109
    _instance = None

    def __new__(cls, canvas=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, canvas=None):
        if self._initialized:
            if canvas is not None:
                self.canvas = canvas
            return
        self.canvas = canvas
        self.pcshape: list[Shape | None] | None = self._create_storage()
        self.shape_count = 0
        self.selected_index: int | None = None
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
        self._initialized = True
        self.start_point_editor()

    def _create_storage(self) -> list[Shape | None]:
        storage: list[Shape | None] = []
        storage.extend([None] * self.MAX_SHAPES)
        return storage

    @classmethod
    def get_instance(cls, canvas=None):
        if cls._instance is None:
            cls._instance = cls(canvas)
        elif canvas is not None:
            cls._instance.canvas = canvas
        return cls._instance

    @classmethod
    def has_instance(cls):
        return cls._instance is not None and cls._instance.is_alive

    def destroy(self):
        if not self.is_alive:
            return
        self.clear_rubber_band()
        if self.pcshape is not None:
            for i in range(self.MAX_SHAPES):
                self.pcshape[i] = None
            self.pcshape = None
        self.shape_count = 0
        self.selected_index = None
        self.current_shape_cls = None
        self.preview_shape = None
        self.canvas = None
        self.is_alive = False
        self._initialized = False
        if MyEditor._instance is self:
            MyEditor._instance = None

    def start(self, shape_cls, shape_name):
        if not self.is_alive:
            return
        self.clear_rubber_band()
        self.is_drawing = False
        self.current_shape_cls = shape_cls
        self.preview_shape = shape_cls()
        self.current_type = shape_name

    def start_point_editor(self):
        self.start(PointShape, PointShape.DISPLAY_NAME)

    def start_line_editor(self):
        self.start(LineShape, LineShape.DISPLAY_NAME)

    def start_rect_editor(self):
        self.start(RectShape, RectShape.DISPLAY_NAME)

    def start_ellipse_editor(self):
        self.start(EllipseShape, EllipseShape.DISPLAY_NAME)

    def start_line_oo_editor(self):
        self.start(LineOOShape, LineOOShape.DISPLAY_NAME)

    def start_cube_editor(self):
        self.start(CubeShape, CubeShape.DISPLAY_NAME)

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

    def set_selected_index(self, index):
        if not self.is_alive:
            return
        self.selected_index = index if (index is not None and 0 <= index < self.shape_count) else None
        self.on_paint()

    def remove_shape_at(self, index):
        if not self.is_alive or self.pcshape is None or not (0 <= index < self.shape_count):
            return False
        for i in range(index, self.shape_count - 1):
            self.pcshape[i] = self.pcshape[i + 1]
        self.pcshape[self.shape_count - 1] = None
        self.shape_count -= 1
        self.selected_index = None
        self.on_paint()
        return True

    def undo_last(self):
        if not self.is_alive or self.pcshape is None or self.shape_count == 0:
            return False
        self.shape_count -= 1
        self.pcshape[self.shape_count] = None
        if self.selected_index is not None and self.selected_index >= self.shape_count:
            self.selected_index = None
        self.on_paint()
        return True

    def clear_all(self):
        if not self.is_alive:
            return
        self.clear_rubber_band()
        self.pcshape = self._create_storage()
        self.shape_count = 0
        self.selected_index = None
        if self.canvas is not None:
            self.canvas.delete("all")

    def clear_rubber_band(self):
        if self.canvas is not None:
            for item_id in self.rubber_ids:
                self.canvas.delete(item_id)
        self.rubber_ids.clear()

    def get_table_rows(self):
        rows = []
        if not self.is_alive or self.pcshape is None:
            return rows
        for i in range(self.shape_count):
            shape = self.pcshape[i]
            if shape is not None:
                x1, y1, x2, y2 = shape.get_coords()
                rows.append((shape.get_display_name(), x1, y1, x2, y2))
        return rows

    def save_to_file(self, filepath):
        if not self.is_alive or self.pcshape is None:
            return 0
        saved = 0
        with open(filepath, "w", encoding="utf-8") as f:
            for i in range(self.shape_count):
                shape = self.pcshape[i]
                if shape is not None:
                    f.write(shape.serialize() + "\n")
                    saved += 1
        return saved

    def load_from_file(self, filepath):
        if not self.is_alive:
            return 0
        loaded_shapes = []
        with open(filepath, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                if len(loaded_shapes) >= self.MAX_SHAPES:
                    break
                loaded_shapes.append(Shape.deserialize(line))
        self.clear_all()
        for shape in loaded_shapes:
            self.add_shape(shape)
        self.on_paint()
        return len(loaded_shapes)

    def on_lb_down(self, x, y):
        if not self.is_alive:
            return
        self.is_drawing = True
        self.start_x, self.start_y = x, y
        self.current_x, self.current_y = x, y

    def on_mouse_move(self, x, y):
        if not self.is_alive or not self.is_drawing or self.preview_shape is None:
            return
        self.current_x, self.current_y = x, y
        self.clear_rubber_band()
        self.preview_shape.set_coords(self.start_x, self.start_y, self.current_x, self.current_y)
        self.rubber_ids = self.preview_shape.show_rubber_band(self.canvas)

    def on_lb_up(self, x, y):
        if not self.is_alive or not self.is_drawing:
            return None
        self.current_x, self.current_y = x, y
        self.is_drawing = False
        self.clear_rubber_band()
        created_shape = None
        if self.current_shape_cls is not None:
            shape = self.current_shape_cls(self.start_x, self.start_y, self.current_x, self.current_y)
            if self.add_shape(shape):
                created_shape = shape
        self.on_paint()
        return created_shape

    def on_paint(self):
        if not self.is_alive or self.canvas is None or self.pcshape is None:
            return
        self.canvas.delete("all")
        for i in range(self.shape_count):
            shape = self.pcshape[i]
            if shape is not None:
                shape.show(self.canvas)
                if self.selected_index == i:
                    shape.show_selected(self.canvas)
