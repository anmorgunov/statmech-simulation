import numpy as np
import constants
from make_figures import FigureMaker
from scipy.optimize import curve_fit
from tqdm import tqdm

class Grid:
    def __init__(self, width, height, cell_size):
        self.cell_size = cell_size
        self.cols = int(width / cell_size)
        self.rows = int(height / cell_size)
        self.cells = [[[] for _ in range(self.cols)] for _ in range(self.rows)]

    def add_particle(self, particle):
        col = min(int(particle.x // self.cell_size), self.cols - 1)
        row = min(int(particle.y // self.cell_size), self.rows - 1)
        # print(f"{row=}, {col=}, {self.rows=}, {self.cols=}")
        self.cells[row][col].append(particle)

    def get_nearby_particles(self, particle):
        col = int(particle.x / self.cell_size)
        row = int(particle.y / self.cell_size)
        nearby_particles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_row = row + i
                new_col = col + j
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    nearby_particles.extend(self.cells[new_row][new_col])
        return nearby_particles

class Particle:
    def __init__(self, x: float, y: float, element: str, mass:float):
        self.x = x
        self.y = y
        self.element = element
        self.angle = 2 * np.pi * np.random.uniform(0,1)  # Random direction
        initial_speed = constants.MOST_PROBABLE_SPEED(constants.BASE_TEMP, 1) # constants.BASE_SPEED
        self.vx = initial_speed * np.cos(self.angle)
        self.vy = initial_speed * np.sin(self.angle)
        self.mass = 1 #mass

    def move(self):
        # Update position based on velocity
        self.x += self.vx
        self.y += self.vy

        # Boundary checks and reflection for walls
        if (
            self.x <= constants.PARTICLE_RADIUS
            or self.x >= constants.WIDTH - constants.PARTICLE_RADIUS
        ):
            self.vx = -self.vx
        if (
            self.y <= constants.PARTICLE_RADIUS
            or self.y >= constants.HEIGHT - constants.PARTICLE_RADIUS
        ):
            self.vy = -self.vy

    def check_collisions(self, other):
        # Check collision with another particle
        dx = self.x - other.x
        dy = self.y - other.y
        distance = np.sqrt(dx**2 + dy**2)
        if distance < 2 * constants.PARTICLE_RADIUS:
            # Compute the normalized normal vector
            nx = dx / distance
            ny = dy / distance

            # Compute the relative velocity
            dvx = self.vx - other.vx
            dvy = self.vy - other.vy

            # Compute the dot product of the relative velocity and the normal
            dot_product = dvx * nx + dvy * ny

            # Check if particles are moving towards each other
            if dot_product > 0:
                return

            # Compute the collision impulse
            impulse = (2 * other.mass) / (self.mass + other.mass) * dot_product

            # Update velocities based on the impulse
            self.vx -= impulse * nx
            self.vy -= impulse * ny
            other.vx += impulse * nx
            other.vy += impulse * ny

    def render(self):
        return {
            "x": self.x,
            "y": self.y,
            "color": constants.ATOMS_LIBRARY["color"][self.element],
            # "element": self.element
        }


class Game:
    def __init__(self, num_particles):
        self.particles = []
        self.atomToCount = {}
        y_high_offset = -constants.PARTICLE_RADIUS*2
        y_low_offset = constants.PARTICLE_RADIUS*2
        for _ in range(num_particles):
            if np.random.rand(1) < 0.5:
                x_low_offset = constants.WIDTH // 2 + constants.PARTICLE_RADIUS*2
                x_high_offset = -constants.PARTICLE_RADIUS*2
                element = "O"
            else:
                x_low_offset = constants.PARTICLE_RADIUS*2
                x_high_offset = -constants.WIDTH // 2 - constants.PARTICLE_RADIUS*2
                element = "C"
            self.atomToCount[element] = self.atomToCount.get(element, 0) + 1
            x = np.random.uniform(x_low_offset, x_high_offset + constants.WIDTH)
            y = np.random.uniform(y_low_offset, y_high_offset + constants.HEIGHT)
            self.particles.append(Particle(x=x, y=y, element=element, mass=constants.ATOMS_LIBRARY["mass"][element]))
        print("Initialized the following atom counts: ", self.atomToCount)
        self.left_fraction = 0
        self.right_fraction = 0
        self.left_fractions = []
        self.right_fractions = []
        self.time = 0
        self.elementToT = {"equipartition": {}, "boltzmann": {}}
        self.update_compartment_fractions()
        self.compute_velocity_distribution(initialization=True)
        self.find_equipartition_temperature()

    def reset(self):
        self.__init__(len(self.particles))

    def update_compartment_fractions(self):
        left_count = sum(
            1 for p in self.particles if p.x < constants.WIDTH / 2 and p.element == "O"
        )
        right_count = sum(
            1 for p in self.particles if p.x >= constants.WIDTH / 2 and p.element == "O"
        )
        self.left_fraction = np.round(100 * left_count / (left_count + right_count), 2)
        self.right_fraction = np.round(100 * right_count / (left_count + right_count), 2)
        self.left_fractions.append(self.left_fraction)
        self.right_fractions.append(self.right_fraction)

    def compute_velocity_distribution(self, initialization=False):
        self.abs_velocities = [np.sqrt(p.vx**2 + p.vy**2) for p in self.particles]
        self.x_velocities = [p.vx**2 for p in self.particles]
        self.y_velocities = [p.vy**2 for p in self.particles]

        for prefix, data in [("abs", self.abs_velocities), ("x", self.x_velocities), ("y", self.y_velocities)]:
            self.bin_velocities(velocities=data, bin_count=10, prefix=prefix, initialization=initialization)

    def bin_velocities(self, velocities, bin_count, prefix, initialization=False):
        if initialization:
            bins = np.array([0] * bin_count)
            bins[bin_count // 2] = len(velocities)  # Put all counts in the middle bin
            value = velocities[0]
            bin_ranges = [(value, value) for _ in range(bin_count)]
        else:
            bins, edges = np.histogram(velocities, bins=bin_count, density=True)
            # Convert bin edges to bin ranges for better clarity on the frontend
            bin_ranges = [(edges[i], edges[i+1]) for i in range(bin_count)]
        setattr(self, f"{prefix}_velocities_bins", bins.tolist())
        setattr(self, f"{prefix}_velocities_bin_ranges", bin_ranges)

    def find_equipartition_temperature(self):
        elementToSum = {}
        for particle in self.particles:
            elementToSum.setdefault(particle.element, []).append(particle.vx**2 + particle.vy**2)
        for element, sums in elementToSum.items():
            self.elementToT["equipartition"].setdefault(element, []).append(constants.TEMP_CONVERSION_FACTOR * 1/(3 * constants.BOLTZMANN) * (particle.mass/(1000 * constants.AVOGADRO)) * np.mean(sums))

    def _maxwell_boltzmann_distribution(self, m):
        return lambda v2, T: 4 * np.pi * (m/(2 * np.pi * constants.BOLTZMANN * T))**(3/2) * v2 * np.exp(-m * v2/(2 * constants.BOLTZMANN * T))

    def find_maxwell_boltzmann_temperature(self):
        elementToSum = {}
        for particle in self.particles:
            elementToSum.setdefault(particle.element, []).append(particle.vx**2 + particle.vy**2)

        for element, velocities in elementToSum.items():
            hist, bin_edges = np.histogram(velocities, bins=20, density=True)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

            # Fit the Maxwell-Boltzmann distribution to the histogram
            abs_mass = 1 / (1000 * constants.AVOGADRO) # constants.ATOMS_LIBRARY["mass"][element]
            popt, _ = curve_fit(self._maxwell_boltzmann_distribution(abs_mass), bin_centers, hist)
            self.elementToT["boltzmann"][element] = popt[0]

    def update(self):
        self.time += 1
        grid = Grid(constants.WIDTH, constants.HEIGHT, int(5 * constants.PARTICLE_RADIUS))

        # Add particles to grid
        for particle in self.particles:
            particle.move()
            grid.add_particle(particle)

        # Collision resolution using grid
        for particle in self.particles:
            nearby_particles = grid.get_nearby_particles(particle)
            for other in nearby_particles:
                if particle != other:
                    particle.check_collisions(other)

        # Collision resolution
        # for i in range(len(self.particles)):
        #     for j in range(i + 1, len(self.particles)):
        #         self.particles[i].check_collisions(self.particles[j])

        self.update_compartment_fractions()
        self.compute_velocity_distribution()
        self.find_equipartition_temperature()
        # self.find_maxwell_boltzmann_temperature()

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
        }
        for element, t in self.elementToT["equipartition"].items():
            data[f"{element.lower()}_equipartition_temperature"] = "{:.2f}".format(np.round(t[-1], 2))
        # for element, t in self.elementToT["boltzmann"].items():
        #     data[f"{element.lower()}_boltzmann_temperature"] = "{:.2f}".format(np.round(t, 2))
        return data

    def analyze_game(self):
        figs = FigureMaker()
        figs.create_fractions_scatter_plot(self.left_fractions, self.right_fractions)
        figs.create_equipartition_scatter_plot(self.elementToT["equipartition"])

if __name__ == "__main__":
    game = Game(200)
    for _ in tqdm(range(10_000)):
        game.update()
    game.analyze_game()
    # print(game.export())