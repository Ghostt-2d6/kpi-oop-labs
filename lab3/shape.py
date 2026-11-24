from abc import ABC, abstractmethod


class Shape(ABC):
    def __init__(self, xs1=0, ys1=0, xs2=0, ys2=0):
        self.xs1 = xs1
        self.ys1 = ys1
        self.xs2 = xs2
        self.ys2 = ys2

    def set_coords(self, x1, y1, x2, y2):
        self.xs1 = x1
        self.ys1 = y1
        self.xs2 = x2
        self.ys2 = y2

    @abstractmethod
    def show(self, canvas):
        pass


class PointShape(Shape):
    def show(self, canvas):
        r = 2
        canvas.create_oval(self.xs1 - r, self.ys1 - r, self.xs1 + r, self.ys1 + r, fill="black", outline="black")


class LineShape(Shape):
    def show(self, canvas):
        canvas.create_line(self.xs1, self.ys1, self.xs2, self.ys2, fill="black", width=1)


class RectShape(Shape):
    def show(self, canvas):
        x1 = 2 * self.xs1 - self.xs2
        y1 = 2 * self.ys1 - self.ys2
        canvas.create_rectangle(x1, y1, self.xs2, self.ys2, outline="black", fill="", width=1)


class EllipseShape(Shape):
    def show(self, canvas):
        canvas.create_oval(self.xs1, self.ys1, self.xs2, self.ys2, outline="black", fill="#87CEEB", width=1)