from abc import ABC, abstractmethod
from point_shape import PointShape
from line_shape import LineShape
from rect_shape import RectShape
from ellipse_shape import EllipseShape


class Editor(ABC):
    @abstractmethod
    def on_lb_down(self, x, y):
        pass

    @abstractmethod
    def on_lb_up(self, x, y):
        pass

    @abstractmethod
    def on_mouse_move(self, x, y):
        pass

    @abstractmethod
    def on_paint(self):
        pass


class ShapeObjectsEditor(Editor):
    N = 108

    def __init__(self, canvas):
        self.canvas = canvas
        self.pcshape = [None] * self.N
        self.shape_count = 0
        self.current_shape = None
        self.current_type = "Прямокутник"
        self.is_drawing = False
        self.rubber_item = None
        self.start_x = 0
        self.start_y = 0

    def set_shape_type(self, shape_type):
        self.current_type = shape_type

    def create_shape(self):
        if self.current_type == "Крапка":
            return PointShape()
        if self.current_type == "Лінія":
            return LineShape()
        if self.current_type == "Прямокутник":
            return RectShape()
        if self.current_type == "Еліпс":
            return EllipseShape()
        return None

    def on_lb_down(self, x, y):
        if self.shape_count >= self.N:
            return
        self.current_shape = self.create_shape()
        if self.current_shape is None:
            return
        self.is_drawing = True
        self.start_x = x
        self.start_y = y
        self.current_shape.set_coords(x, y, x, y)
        self.rubber_item = self.current_shape.draw_rubber_band(self.canvas)

    def on_mouse_move(self, x, y):
        if not self.is_drawing or self.current_shape is None:
            return
        if self.rubber_item is not None:
            self.canvas.delete(self.rubber_item)
        self.current_shape.set_coords(self.start_x, self.start_y, x, y)
        self.rubber_item = self.current_shape.draw_rubber_band(self.canvas)

    def on_lb_up(self, x, y):
        if not self.is_drawing or self.current_shape is None:
            return
        if self.rubber_item is not None:
            self.canvas.delete(self.rubber_item)
            self.rubber_item = None
        self.current_shape.set_coords(self.start_x, self.start_y, x, y)
        self.pcshape[self.shape_count] = self.current_shape
        self.shape_count += 1
        self.current_shape = None
        self.is_drawing = False
        self.on_paint()

    def on_paint(self):
        self.canvas.delete("all")
        for i in range(self.shape_count):
            if self.pcshape[i] is not None:
                self.pcshape[i].show(self.canvas)

    def clear_all(self):
        self.pcshape = [None] * self.N
        self.shape_count = 0
        self.current_shape = None
        self.is_drawing = False
        self.rubber_item = None
        self.on_paint()