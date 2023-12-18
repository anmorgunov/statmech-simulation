import pytest
from .Particle import Particle
from .Grid import Grid

class TestGrid:
    @pytest.mark.parametrize(
        "width, height, cell_size",
        [
            (100, 100, 10),
            (200, 150, 20),
            (300, 300, 30),
        ],
    )
    def test_init(self, width, height, cell_size):
        grid = Grid(width, height, cell_size)
        assert grid.cell_size == cell_size
        assert grid.cols == width // cell_size
        assert grid.rows == height // cell_size
        assert all(len(row) == grid.cols for row in grid.cells)

    def test_add_particle(self):
        width, height, cell_size = 100, 100, 10
        grid = Grid(width, height, cell_size)
        particle = Particle("H", 15, 25, 10, 5, 1, "red")
        grid.add_particle(particle)
        col, row = 1, 2  # Expected column and row based on particle's position
        assert particle in grid.cells[row][col]

    def test_get_nearby_particles(self):
        width, height, cell_size = 100, 100, 10
        grid = Grid(width, height, cell_size)

        # Add several particles
        particles = [
            Particle("H", 15, 25, 10, 5, 1, "red"),
            Particle("He", 35, 25, 10, 5, 1, "blue"),
            Particle("Li", 25, 35, 10, 5, 1, "green"),
        ]
        for particle in particles:
            grid.add_particle(particle)

        # Check nearby particles
        test_particle = Particle("Be", 25, 25, 10, 5, 1, "yellow")
        nearby_particles = grid.get_nearby_particles(test_particle)
        assert len(nearby_particles) == 3
        for particle in particles:
            assert particle in nearby_particles


# Additional tests can be added for edge cases, such as particles on the edge of the grid.
