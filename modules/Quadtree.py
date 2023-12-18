class QuadtreeNode:
    def __init__(self, x, y, width, height, depth=0, max_depth=4):
        self.bounds = (x, y, width, height)
        self.particles = []
        self.children = []
        self.depth = depth
        self.max_depth = max_depth

    def subdivide(self):
        x, y, width, height = self.bounds
        hw, hh = width / 2, height / 2
        self.children = [
            QuadtreeNode(x, y, hw, hh, self.depth + 1, self.max_depth),
            QuadtreeNode(x + hw, y, hw, hh, self.depth + 1, self.max_depth),
            QuadtreeNode(x, y + hh, hw, hh, self.depth + 1, self.max_depth),
            QuadtreeNode(x + hw, y + hh, hw, hh, self.depth + 1, self.max_depth),
        ]

    def insert(self, particle):
        if not self._in_bounds(particle):
            return False

        if len(self.particles) < 4 or self.depth == self.max_depth:
            self.particles.append(particle)
            return True

        if not self.children:
            self.subdivide()

        return any(child.insert(particle) for child in self.children)

    def query(self, range, found_particles):
        if not self._intersects(range):
            return

        for particle in self.particles:
            if self._in_range(particle, range):
                found_particles.append(particle)

        if not self.children:
            return

        for child in self.children:
            child.query(range, found_particles)

    def _in_bounds(self, particle):
        x, y, width, height = self.bounds
        return x <= particle.x < x + width and y <= particle.y < y + height

    def _intersects(self, range):
        x, y, width, height = self.bounds
        rx, ry, rwidth, rheight = range
        return not (
            rx + rwidth < x or rx > x + width or ry + rheight < y or ry > y + height
        )

    def _in_range(self, particle, range):
        px, py = particle.x, particle.y
        rx, ry, rwidth, rheight = range

        # Check if the particle is within the range rectangle
        return (rx <= px <= rx + rwidth) and (ry <= py <= ry + rheight)
