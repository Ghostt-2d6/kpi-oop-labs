from shape import Shape


class LineShape(Shape):
    def show(self, canvas):
        return canvas.create_line(self.xs1, self.ys1, self.xs2, self.ys2, fill="black")

    def draw_rubber_band(self, canvas):
        return canvas.create_line(self.xs1, self.ys1, self.xs2, self.ys2, fill="black")