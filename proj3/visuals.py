import tkinter as tk
import random
import math

class TessellationCanvas:
    def __init__(self, master, width=800, height=600, shape="hex", tile_size=60):
        self.master = master
        self.master.title("Tessellation Canvas")

        self.canvas = tk.Canvas(master, width=width, height=height, bg="white")
        self.canvas.pack()

        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.shape = shape.lower()
        self.shapes = []  # store shape item IDs

        self.generate_tessellation()

    def generate_tessellation(self):
        """Fill the canvas with a tessellation of shapes."""
        self.canvas.delete("all")
        self.shapes.clear()

        if self.shape == "square":
            self._generate_square_grid()
        elif self.shape == "triangle":
            self._generate_triangle_grid()
        else:
            self._generate_hex_grid()

    def _generate_square_grid(self):
        """Create a tessellation of squares."""
        s = self.tile_size
        for y in range(0, self.height, s):
            for x in range(0, self.width, s):
                shape_id = self.canvas.create_rectangle(x, y, x+s, y+s, outline="black", fill="")
                self.shapes.append(shape_id)

    def _generate_triangle_grid(self):
        """Create a tessellation of equilateral triangles."""
        s = self.tile_size
        h = int(s * math.sqrt(3) / 2)
        for row in range(0, self.height // h + 2):
            for col in range(0, self.width // s + 2):
                x = col * s + (s // 2 if row % 2 else 0)
                y = row * h
                points_up = [x, y, x+s//2, y+h, x-s//2, y+h]
                points_down = [x, y+h, x+s//2, y, x-s//2, y]
                points = points_up if (row + col) % 2 == 0 else points_down
                shape_id = self.canvas.create_polygon(points, outline="black", fill="")
                self.shapes.append(shape_id)

    def _generate_hex_grid(self):
        """Create a tessellation of hexagons."""
        r = self.tile_size / 2
        h = math.sqrt(3) * r
        for row in range(int(self.height / h) + 2):
            for col in range(int(self.width / (1.5 * r)) + 2):
                cx = col * 1.5 * r
                cy = row * h + (h / 2 if col % 2 else 0)
                points = self._hexagon_points(cx, cy, r)
                shape_id = self.canvas.create_polygon(points, outline="black", fill="")
                self.shapes.append(shape_id)

    def _hexagon_points(self, cx, cy, r):
        """Return 6 points for a hexagon centered at (cx, cy)."""
        return [
            cx + r * math.cos(math.radians(angle))
            for angle in range(30, 390, 60)
        ], [
            cy + r * math.sin(math.radians(angle))
            for angle in range(30, 390, 60)
        ]

    def fill_random(self, colors):
        """Fill shapes with random colors from a given list."""
        for shape_id in self.shapes:
            color = random.choice(colors)
            self.canvas.itemconfig(shape_id, fill=color)

    def fill_with_colors(self, color_list):
        """Fill shapes in order with colors from external input."""
        for shape_id, color in zip(self.shapes, color_list):
            self.canvas.itemconfig(shape_id, fill=color)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = TessellationCanvas(root, shape="hex", tile_size=80)

    # Example: fill randomly from a palette
    palette = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f"]
    app.fill_random(palette)

    # Example (external input):
    # app.fill_with_colors(["#ff0000", "#00ff00", "#0000ff", ...])

    root.mainloop()
