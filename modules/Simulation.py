import numpy as np
import constants
from scipy.optimize import curve_fit
from tqdm import tqdm

from .Figures import FigureMaker
from .Particle import Particle
from .Grid import Grid
from .utils import phys_constants as cnst

WIDTH = 800
HEIGHT = 500


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


class TwoCompartments:
    def __init__(
        self,
        num_left: int = 50,
        left_atom: str = "C",
        num_right: int = 50,
        right_atom: str = "O",
        temperature: int = 300,
    ):
        self.particles = []
        self.init_params = {
            "num_left": num_left,
            "left_atom": left_atom,
            "num_right": num_right,
            "right_atom": right_atom,
            "temperature": temperature,
        }
        self.max_radius = 0
        bounds = {
            "y": lambda radius: (radius * 2, HEIGHT - radius * 2),
            "left": {
                "x": lambda radius: (radius * 2, WIDTH // 2 - radius * 2),
            },
            "right": {
                "x": lambda radius: (WIDTH // 2 + radius * 2, WIDTH - radius * 2),
            },
        }

        for i in range(num_left + num_right):
            if i < num_left:
                x_compartment = "left"
                atom = left_atom
                special = False
            else:
                x_compartment = "right"
                atom = right_atom
                special = True
            atom_data = cnst.ATOMS_LIBRARY[atom]
            radius = atom_data["radius"] / 10
            self.max_radius = max(self.max_radius, radius)
            likely_speed = cnst.MOST_PROBABLE_SPEED(temperature, atom_data["mass"])

            self.particles.append(
                Particle(
                    element=atom,
                    x=np.random.uniform(*bounds[x_compartment]["x"](radius)),
                    y=np.random.uniform(*bounds["y"](radius)),
                    initial_speed=likely_speed,
                    radius=radius,
                    mass=atom_data["mass"],
                    color=atom_data["color"],
                    special=special,
                )
            )

        self.left_fraction = 0
        self.right_fraction = 0
        self.left_fractions = []
        self.right_fractions = []
        self.time = 0
        self.elementToT = {"equipartition": {}, "boltzmann": {}}
        self.update_compartment_fractions()
        self.compute_velocity_distribution(initialization=True)
        self.find_equipartition_temperature()

        self.quadtree = QuadtreeNode(0, 0, WIDTH, HEIGHT)

    def reset(self):
        self.__init__(**self.init_params)
    
    def _get_query_range(self, particle):
        # Define the query range based on particle position and radius
        # Here we're using a square range centered on the particle
        range_size = particle.radius * 4
        return (particle.x - particle.radius, particle.y - particle.radius,
                range_size, range_size)

    def update(self):
        self.time += 1
        # grid = Grid(WIDTH, HEIGHT, 100)
        self.quadtree = QuadtreeNode(0, 0, WIDTH, HEIGHT)
        # Add particles to grid
        for particle in self.particles:
            particle.move()
            # grid.add_particle(particle)
            self.quadtree.insert(particle)

        for particle in self.particles:
            nearby_particles = []
            self.quadtree.query(self._get_query_range(particle), nearby_particles)
            for other in nearby_particles:
                if other is not particle:
                    particle.check_collision(other)

        # Collision resolution using grid
        # for particle in self.particles:
        #     nearby_particles = grid.get_nearby_particles(particle)
        #     for other in nearby_particles:
        #         if particle is not other:
        #             particle.check_collision(other)

        # Collision resolution
        # for i in range(len(self.particles)):
        #     for j in range(i + 1, len(self.particles)):
        #         self.particles[i].check_collision(self.particles[j])

        self.update_compartment_fractions()
        self.compute_velocity_distribution()
        if self.time % 10 == 0:
            self.find_equipartition_temperature()
        # self.find_maxwell_boltzmann_temperature()

    def update_compartment_fractions(self):
        left_count = sum(1 for p in self.particles if p.x < WIDTH / 2 and p.special)
        right_count = sum(1 for p in self.particles if p.x >= WIDTH / 2 and p.special)
        self.left_fraction = np.round(100 * left_count / (left_count + right_count), 2)
        self.right_fraction = np.round(
            100 * right_count / (left_count + right_count), 2
        )
        self.left_fractions.append(self.left_fraction)
        self.right_fractions.append(self.right_fraction)

    def compute_velocity_distribution(self, initialization=False):
        self.abs_velocities = [np.sqrt(p.vx**2 + p.vy**2) for p in self.particles]
        self.x_velocities = [p.vx**2 for p in self.particles]
        self.y_velocities = [p.vy**2 for p in self.particles]

        for prefix, data in [
            ("abs", self.abs_velocities),
            ("x", self.x_velocities),
            ("y", self.y_velocities),
        ]:
            self.bin_velocities(
                velocities=data,
                bin_count=10,
                prefix=prefix,
                initialization=initialization,
            )

    def bin_velocities(self, velocities, bin_count, prefix, initialization=False):
        if initialization:
            bins = np.array([0] * bin_count)
            bins[bin_count // 2] = len(velocities)  # Put all counts in the middle bin
            value = velocities[0]
            bin_ranges = [(value, value) for _ in range(bin_count)]
        else:
            bins, edges = np.histogram(velocities, bins=bin_count, density=True)
            # Convert bin edges to bin ranges for better clarity on the frontend
            bin_ranges = [(edges[i], edges[i + 1]) for i in range(bin_count)]
        setattr(self, f"{prefix}_velocities_bins", bins.tolist())
        setattr(self, f"{prefix}_velocities_bin_ranges", bin_ranges)

    def find_equipartition_temperature(self):
        elementToSum = {}
        for particle in self.particles:
            elementToSum.setdefault(particle.element, []).append(
                particle.vx**2 + particle.vy**2
            )

        for element, sums in elementToSum.items():
            self.elementToT["equipartition"].setdefault(element, []).append(
                cnst.TEMP_CONVERSION_FACTOR
                * cnst.ATOMS_LIBRARY[element]["mass"]
                / (3 * cnst.R * 1000)
                * np.mean(sums)
            )

    # def _maxwell_boltzmann_distribution(self, m):
    #     return (
    #         lambda v2, T: 4
    #         * np.pi
    #         * (m / (2 * np.pi * constants.BOLTZMANN * T)) ** (3 / 2)
    #         * v2
    #         * np.exp(-m * v2 / (2 * constants.BOLTZMANN * T))
    #     )

    # def find_maxwell_boltzmann_temperature(self):
    #     elementToSum = {}
    #     for particle in self.particles:
    #         elementToSum.setdefault(particle.element, []).append(
    #             particle.vx**2 + particle.vy**2
    #         )

    #     for element, velocities in elementToSum.items():
    #         hist, bin_edges = np.histogram(velocities, bins=20, density=True)
    #         bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    #         # Fit the Maxwell-Boltzmann distribution to the histogram
    #         abs_mass = 1 / (
    #             1000 * constants.AVOGADRO
    #         )  # constants.ATOMS_LIBRARY["mass"][element]
    #         popt, _ = curve_fit(
    #             self._maxwell_boltzmann_distribution(abs_mass), bin_centers, hist
    #         )
    #         self.elementToT["boltzmann"][element] = popt[0]

    def export(self):
        data = {
            "particles": [p.render() for p in self.particles],
            "left_fraction": self.left_fractions[-1],
            "right_fraction": self.right_fractions[-1],
            "abs_velocities_bins": self.abs_velocities_bins,
            "abs_velocities_bin_ranges": self.abs_velocities_bin_ranges,
            "x_velocities_bins": self.x_velocities_bins,
            "x_velocities_bin_ranges": self.x_velocities_bin_ranges,
            "y_velocities_bins": self.y_velocities_bins,
            "y_velocities_bin_ranges": self.y_velocities_bin_ranges,
            "initial_temperature": self.init_params["temperature"],
        }
        for element, t in self.elementToT["equipartition"].items():
            data[f"{element.lower()}_equipartition_temperature"] = "{:.2f}".format(
                np.round(t[-1], 2)
            )
        # for element, t in self.elementToT["boltzmann"].items():
        #     data[f"{element.lower()}_boltzmann_temperature"] = "{:.2f}".format(np.round(t, 2))
        return data

    def analyze_game(self):
        figs = FigureMaker()
        figs.create_fractions_scatter_plot(self.left_fractions, self.right_fractions)
        figs.create_equipartition_scatter_plot(self.elementToT["equipartition"])


if __name__ == "__main__":
    # game = Game(200)
    # for _ in tqdm(range(10_000)):
    #     game.update()
    # game.analyze_game()
    # print(game.export())

    pass
