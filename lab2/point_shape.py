from shape import Shape


class PointShape(Shape):
    def show(self, canvas):
        return canvas.create_oval(self.xs1 - 1, self.ys1 - 1, self.xs1 + 1, self.ys1 + 1, outline="black", fill="black")

    def draw_rubber_band(self, canvas):
        return canvas.create_oval(self.xs2 - 1, self.ys2 - 1, self.xs2 + 1, self.ys2 + 1, outline="black", fill="black")