from .Particle import Particle
from typing import List


class Grid:
    def __init__(self, width: int, height: int, cell_size: int):
        self.cell_size = cell_size
        self.cols = int(width / cell_size)
        self.rows = int(height / cell_size)
        self.cells = [[[] for _ in range(self.cols)] for _ in range(self.rows)]

    def add_particle(self, particle: Particle):
        col = min(int(particle.x // self.cell_size), self.cols - 1)
        row = min(int(particle.y // self.cell_size), self.rows - 1)
        self.cells[row][col].append(particle)

    def get_nearby_particles(self, particle: Particle) -> List[Particle]:
        col = min(int(particle.x // self.cell_size), self.cols - 1)
        row = min(int(particle.y // self.cell_size), self.rows - 1)
        nearby_particles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_row = row + i
                new_col = col + j
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    nearby_particles.extend(self.cells[new_row][new_col])
        return nearby_particles
