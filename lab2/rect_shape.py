from shape import Shape


class RectShape(Shape):
    def show(self, canvas):
        return canvas.create_rectangle(self.xs1, self.ys1, self.xs2, self.ys2, outline="black", fill="")

    def draw_rubber_band(self, canvas):
        return canvas.create_rectangle(self.xs1, self.ys1, self.xs2, self.ys2, outline="black", fill="")