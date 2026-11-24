from abc import ABC, abstractmethod
from shape import PointShape, LineShape, RectShape, EllipseShape


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


class ShapeEditor(Editor):
    VARIANT_Z = 9
    MAX_SHAPES = VARIANT_Z + 100

    def __init__(self, canvas, pcshape=None, count=0):
        self.canvas = canvas
        self.pcshape = [None] * self.MAX_SHAPES if pcshape is None else pcshape
        self.shape_count = count
        self.is_drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.rubber_id = None

    def get_storage(self):
        return self.pcshape, self.shape_count

    def set_storage(self, pcshape, count):
        self.pcshape = pcshape
        self.shape_count = count

    def add_shape(self, shape):
        if self.shape_count < self.MAX_SHAPES:
            self.pcshape[self.shape_count] = shape
            self.shape_count += 1
            return True
        return False

    def undo_last(self):
        if self.shape_count > 0:
            self.shape_count -= 1
            self.pcshape[self.shape_count] = None
            self.on_paint()
            return True
        return False

    def clear_rubber_band(self):
        if self.rubber_id is not None:
            self.canvas.delete(self.rubber_id)
            self.rubber_id = None

    def on_lb_down(self, x, y):
        self.is_drawing = True
        self.start_x = x
        self.start_y = y
        self.current_x = x
        self.current_y = y

    def on_mouse_move(self, x, y):
        if not self.is_drawing:
            return
        self.current_x = x
        self.current_y = y
        self.clear_rubber_band()
        self.draw_rubber_band()

    @abstractmethod
    def draw_rubber_band(self):
        pass

    @abstractmethod
    def create_shape(self):
        pass

    def on_lb_up(self, x, y):
        if not self.is_drawing:
            return
        self.current_x = x
        self.current_y = y
        self.is_drawing = False
        self.clear_rubber_band()
        shape = self.create_shape()
        if shape is not None:
            self.add_shape(shape)
        self.on_paint()

    def on_paint(self):
        self.canvas.delete("all")
        for i in range(self.shape_count):
            if self.pcshape[i] is not None:
                self.pcshape[i].show(self.canvas)


class PointEditor(ShapeEditor):
    def draw_rubber_band(self):
        r = 2
        self.rubber_id = self.canvas.create_oval(
            self.current_x - r, self.current_y - r, self.current_x + r, self.current_y + r,
            outline="red", fill="red", width=1
        )

    def create_shape(self):
        return PointShape(self.current_x, self.current_y, self.current_x, self.current_y)


class LineEditor(ShapeEditor):
    def draw_rubber_band(self):
        self.rubber_id = self.canvas.create_line(
            self.start_x, self.start_y, self.current_x, self.current_y, fill="red", width=1
        )

    def create_shape(self):
        return LineShape(self.start_x, self.start_y, self.current_x, self.current_y)


class RectEditor(ShapeEditor):
    def draw_rubber_band(self):
        x1 = 2 * self.start_x - self.current_x
        y1 = 2 * self.start_y - self.current_y
        self.rubber_id = self.canvas.create_rectangle(
            x1, y1, self.current_x, self.current_y, outline="red", fill="", width=1
        )

    def create_shape(self):
        return RectShape(self.start_x, self.start_y, self.current_x, self.current_y)


class EllipseEditor(ShapeEditor):
    def draw_rubber_band(self):
        self.rubber_id = self.canvas.create_oval(
            self.start_x, self.start_y, self.current_x, self.current_y, outline="red", fill="", width=1
        )

    def create_shape(self):
        return EllipseShape(self.start_x, self.start_y, self.current_x, self.current_y)