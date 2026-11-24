from shape import Shape


class EllipseShape(Shape):
    def show(self, canvas):
        dx = abs(self.xs2 - self.xs1)
        dy = abs(self.ys2 - self.ys1)
        return canvas.create_oval(self.xs1 - dx, self.ys1 - dy, self.xs1 + dx, self.ys1 + dy, outline="black", fill="#90EE90")

    def draw_rubber_band(self, canvas):
        dx = abs(self.xs2 - self.xs1)
        dy = abs(self.ys2 - self.ys1)
        return canvas.create_oval(self.xs1 - dx, self.ys1 - dy, self.xs1 + dx, self.ys1 + dy, outline="black", fill="")