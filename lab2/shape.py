from abc import ABC, abstractmethod


class Shape(ABC):
    def __init__(self):
        self.xs1 = 0
        self.ys1 = 0
        self.xs2 = 0
        self.ys2 = 0

    def set_coords(self, x1, y1, x2, y2):
        self.xs1 = x1
        self.ys1 = y1
        self.xs2 = x2
        self.ys2 = y2

    @abstractmethod
    def show(self, canvas):
        pass

    @abstractmethod
    def draw_rubber_band(self, canvas):
        pass