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

    @abstractmethod
    def show_rubber_band(self, canvas) -> list:
        return []


class PointShape(Shape):
    def show(self, canvas):
        r = 2
        canvas.create_oval(
            self.xs1 - r, self.ys1 - r, self.xs1 + r, self.ys1 + r,
            fill="black", outline="black"
        )

    def show_rubber_band(self, canvas):
        r = 3
        item_id = canvas.create_oval(
            self.xs2 - r, self.ys2 - r, self.xs2 + r, self.ys2 + r,
            outline="red", fill="", dash=(4, 3), width=1
        )
        return [item_id]


class LineShape(Shape):
    def __init__(self, xs1=0, ys1=0, xs2=0, ys2=0, line_color="black"):
        super().__init__(xs1, ys1, xs2, ys2)
        self.line_color = line_color

    def show(self, canvas):
        canvas.create_line(
            self.xs1, self.ys1, self.xs2, self.ys2,
            fill=self.line_color, width=1
        )

    def show_rubber_band(self, canvas):
        item_id = canvas.create_line(
            self.xs1, self.ys1, self.xs2, self.ys2,
            fill="red", dash=(5, 3), width=1
        )
        return [item_id]


class RectShape(Shape):
    def __init__(self, xs1=0, ys1=0, xs2=0, ys2=0, outline_color="black", fill_color=""):
        super().__init__(xs1, ys1, xs2, ys2)
        self.outline_color = outline_color
        self.fill_color = fill_color

    def show(self, canvas):
        x1 = 2 * self.xs1 - self.xs2
        y1 = 2 * self.ys1 - self.ys2
        canvas.create_rectangle(
            x1, y1, self.xs2, self.ys2,
            outline=self.outline_color, fill=self.fill_color, width=1
        )

    def show_rubber_band(self, canvas):
        x1 = 2 * self.xs1 - self.xs2
        y1 = 2 * self.ys1 - self.ys2
        item_id = canvas.create_rectangle(
            x1, y1, self.xs2, self.ys2,
            outline="red", fill="", dash=(5, 3), width=1
        )
        return [item_id]


class EllipseShape(Shape):
    def __init__(self, xs1=0, ys1=0, xs2=0, ys2=0, outline_color="black", fill_color="#87CEEB"):
        super().__init__(xs1, ys1, xs2, ys2)
        self.outline_color = outline_color
        self.fill_color = fill_color

    def show(self, canvas):
        canvas.create_oval(
            self.xs1, self.ys1, self.xs2, self.ys2,
            outline=self.outline_color, fill=self.fill_color, width=1
        )

    def show_rubber_band(self, canvas):
        item_id = canvas.create_oval(
            self.xs1, self.ys1, self.xs2, self.ys2,
            outline="red", fill="", dash=(5, 3), width=1
        )
        return [item_id]


class LineOOShape(LineShape, EllipseShape):
    def __init__(
        self, xs1=0, ys1=0, xs2=0, ys2=0,
        line_color="#1E3A8A", circle_outline="#1E3A8A",
        circle_fill="#FFD166", radius=8
    ):
        LineShape.__init__(self, xs1, ys1, xs2, ys2, line_color=line_color)
        EllipseShape.__init__(
            self, xs1, ys1, xs2, ys2,
            outline_color=circle_outline, fill_color=circle_fill
        )
        self.radius = radius

    def show(self, canvas):
        x1, y1, x2, y2 = self.xs1, self.ys1, self.xs2, self.ys2
        r = self.radius
        LineShape.show(self, canvas)
        self.set_coords(x1 - r, y1 - r, x1 + r, y1 + r)
        EllipseShape.show(self, canvas)
        self.set_coords(x2 - r, y2 - r, x2 + r, y2 + r)
        EllipseShape.show(self, canvas)
        self.set_coords(x1, y1, x2, y2)

    def show_rubber_band(self, canvas):
        r = self.radius
        line_id = canvas.create_line(
            self.xs1, self.ys1, self.xs2, self.ys2,
            fill="red", dash=(5, 3), width=1
        )
        c1_id = canvas.create_oval(
            self.xs1 - r, self.ys1 - r, self.xs1 + r, self.ys1 + r,
            outline="red", fill="", dash=(5, 3), width=1
        )
        c2_id = canvas.create_oval(
            self.xs2 - r, self.ys2 - r, self.xs2 + r, self.ys2 + r,
            outline="red", fill="", dash=(5, 3), width=1
        )
        return [line_id, c1_id, c2_id]


class CubeShape(RectShape, LineShape):
    def __init__(self, xs1=0, ys1=0, xs2=0, ys2=0, edge_color="#2E5B88"):
        RectShape.__init__(
            self, xs1, ys1, xs2, ys2,
            outline_color=edge_color, fill_color=""
        )
        LineShape.__init__(self, xs1, ys1, xs2, ys2, line_color=edge_color)

    def _compute_cube_parts(self):
        x1, y1, x2, y2 = self.xs1, self.ys1, self.xs2, self.ys2
        dx = (x2 - x1) * 0.35
        dy = -abs(y2 - y1) * 0.35 if y2 != y1 else -abs(x2 - x1) * 0.35
        fcx = (x1 + x2) / 2
        fcy = (y1 + y2) / 2
        bcx = fcx + dx
        bcy = fcy + dy
        edges = [
            ((x1, y1), (x1 + dx, y1 + dy)),
            ((x2, y1), (x2 + dx, y1 + dy)),
            ((x2, y2), (x2 + dx, y2 + dy)),
            ((x1, y2), (x1 + dx, y2 + dy))
        ]
        return (fcx, fcy, x2, y2), (bcx, bcy, x2 + dx, y2 + dy), edges

    def show(self, canvas):
        x1, y1, x2, y2 = self.xs1, self.ys1, self.xs2, self.ys2
        front_rect, back_rect, edges = self._compute_cube_parts()
        self.set_coords(*front_rect)
        RectShape.show(self, canvas)
        self.set_coords(*back_rect)
        RectShape.show(self, canvas)
        for p1, p2 in edges:
            self.set_coords(p1[0], p1[1], p2[0], p2[1])
            LineShape.show(self, canvas)
        self.set_coords(x1, y1, x2, y2)

    def show_rubber_band(self, canvas):
        x1, y1, x2, y2 = self.xs1, self.ys1, self.xs2, self.ys2
        _, back_rect, edges = self._compute_cube_parts()
        dx = back_rect[2] - x2
        dy = back_rect[3] - y2
        items = [
            canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="red", fill="", dash=(5, 3), width=1
            ),
            canvas.create_rectangle(
                x1 + dx, y1 + dy, x2 + dx, y2 + dy,
                outline="red", fill="", dash=(5, 3), width=1
            )
        ]
        for p1, p2 in edges:
            items.append(
                canvas.create_line(
                    p1[0], p1[1], p2[0], p2[1],
                    fill="red", dash=(5, 3), width=1
                )
            )
        return items