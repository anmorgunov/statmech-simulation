import numpy as np
from scipy.optimize import curve_fit
from tqdm import tqdm
from typing import Optional, List, Tuple

from .Figures import FigureMaker
from .Particle import Particle
from .Grid import Grid
from .Quadtree import QuadtreeNode
from .EnergyWall import EnergyWall
from .utils import phys_constants as cnst
from .utils import significance as stat_signif

WIDTH = 800
HEIGHT = 500

from datetime import datetime


def get_timestamp():
    current_datetime = datetime.now()
    return current_datetime.strftime("%Y-%m-%d %H:%M")


class ParticleIterable:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __iter__(self):
        for particle in self.left:
            yield particle
        for particle in self.right:
            yield particle

    def __len__(self):
        return len(self.left) + len(self.right)

    def __getitem__(self, index):
        if index < len(self.left):
            return self.left[index]
        else:
            return self.right[index - len(self.left)]


class TwoCompartments:
    def __init__(
        self,
        num_left: int = 50,
        left_atom: str = "C",
        num_right: int = 50,
        right_atom: str = "O",
        left_temperature: int = 300,
        right_temperature: int = 300,
        use_quadtree: bool = False,
        update_frequency: int = 100,
        rigid_wall: bool = False,
    ):
        self.max_mass = max(
            cnst.ATOMS_LIBRARY[atom]["mass"] for atom in [left_atom, right_atom]
        )

        self.min_temp = min(left_temperature, right_temperature)
        self.max_temp = max(left_temperature, right_temperature)
        self.rigid_wall = rigid_wall
        if rigid_wall:
            self.energy_wall = EnergyWall(WIDTH // 2)
        self.init_params = {
            "num_left": num_left,
            "left_atom": left_atom,
            "num_right": num_right,
            "right_atom": right_atom,
            "left_temperature": left_temperature,
            "right_temperature": right_temperature,
            "use_quadtree": use_quadtree,
            "update_frequency": update_frequency,
            "rigid_wall": rigid_wall,
        }
        self.elToDir = {left_atom: "left", right_atom: "right"}
        self.num_left = num_left
        self.left_atom = left_atom
        self.num_right = num_right
        self.right_atom = right_atom

        self.v_mp_freq = 2
        self.use_quadtree = use_quadtree
        self.update_frequency = update_frequency
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

        self.left_particles = []
        self.right_particles = []
        self.particlesStyle = {}
        for i in range(num_left + num_right):
            if i < num_left:
                x_compartment = "left"
                atom = left_atom
                special = False
                container = self.left_particles
                temperature = left_temperature
            else:
                x_compartment = "right"
                atom = right_atom
                special = True
                container = self.right_particles
                temperature = right_temperature
            atom_data = cnst.ATOMS_LIBRARY[atom]
            radius = atom_data["radius"] / 10
            self.max_radius = max(self.max_radius, radius)
            likely_speed = cnst.MOST_PROBABLE_SPEED(temperature, atom_data["mass"])
            self.particlesStyle[f"{x_compartment}_radius"] = radius
            self.particlesStyle[f"{x_compartment}_color"] = atom_data["color"]
            self.particlesStyle[f"{x_compartment}_soft"] = atom_data["soft_color"]
            self.particlesStyle[f"{x_compartment}_name"] = atom

            container.append(
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
        self.unifpVals = {"chi": [], "chi-rel": [], "ks": []}
        self.velocity_angles = []
        self.bin_edges = None
        self.update_compartment_fractions()
        self.find_equipartition_temperature()
        self.compute_velocity_distribution(initialization=True)
        self.update_v_mp_freq()
        self.assess_uniformity()

        if self.use_quadtree:
            self.quadtree = QuadtreeNode(0, 0, WIDTH, HEIGHT)

    @property
    def particles(self):
        return ParticleIterable(self.left_particles, self.right_particles)

    def reset(self):
        self.__init__(**self.init_params)

    def _get_query_range(self, particle):
        # Define the query range based on particle position and radius
        # Here we're using a square range centered on the particle
        range_size = particle.radius * 3
        return (
            particle.x - particle.radius,
            particle.y - particle.radius,
            range_size,
            range_size,
        )

    def update(self):
        self.time += 1

        if self.use_quadtree:
            self.quadtree = QuadtreeNode(0, 0, WIDTH, HEIGHT)

        for particle in self.particles:
            particle.move()
            if self.rigid_wall:
                particle.check_wall_collision(self.energy_wall)
            if self.use_quadtree:
                self.quadtree.insert(particle)

        if self.use_quadtree:
            for particle in self.particles:
                nearby_particles = []
                self.quadtree.query(self._get_query_range(particle), nearby_particles)
                for other in nearby_particles:
                    if other is not particle:
                        particle.check_collision(other)

        else:
            for i in range(len(self.particles)):
                for j in range(i + 1, len(self.particles)):
                    self.particles[i].check_collision(self.particles[j])

        if self.time % self.update_frequency == 0:
            self.update_compartment_fractions()
            self.find_equipartition_temperature()
            self.compute_velocity_distribution()
            self.assess_uniformity()
            self.update_v_mp_freq()
            # self.time = 0

    def update_compartment_fractions(self):
        left_count = sum(1 for p in self.particles if p.x < WIDTH / 2 and p.special)
        right_count = sum(1 for p in self.particles if p.x >= WIDTH / 2 and p.special)
        self.left_fraction = np.round(100 * left_count / (left_count + right_count), 2)
        self.right_fraction = np.round(
            100 * right_count / (left_count + right_count), 2
        )
        self.left_fractions.append(self.left_fraction)
        self.right_fractions.append(self.right_fraction)

    def compute_velocity_distribution(self, initialization: bool = False):
        assert self.elementToSpeed, "Must call find_equipartition_temperature first"
        if not initialization and self.bin_edges is None:
            min_v, max_v = float("inf"), float("-inf")
            for container in self.elementToSpeed.values():
                for speed in container:
                    min_v = min(min_v, speed)
                    max_v = max(max_v, speed)

            self.bin_edges = np.linspace(min_v, max_v, 11)

        for prefix, data in [
            ("abs_left", self.elementToSpeed[self.left_atom]),
            ("abs_right", self.elementToSpeed[self.right_atom]),
        ]:
            self.bin_velocities(
                velocities=data,
                bin_count=self.bin_edges,
                prefix=prefix,
                initialization=initialization,
            )

    def bin_velocities(
        self, velocities, bin_count, prefix, initialization=False, normalize=True
    ):
        if initialization:
            bins = np.array([0] * 10)
            bins[10 // 2] = len(velocities)  # Put all counts in the middle bin
            value = velocities[0]
            bin_ranges = [(value, value) for _ in range(10)]
        else:
            bins, edges = np.histogram(velocities, bins=bin_count, density=normalize)
            # Convert bin edges to bin ranges for better clarity on the frontend
            if isinstance(bin_count, int):
                bin_ranges = [(edges[i], edges[i + 1]) for i in range(bin_count)]
            else:
                bin_ranges = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]
        setattr(self, f"{prefix}_velocities_bins", bins.tolist())
        setattr(self, f"{prefix}_velocities_bin_ranges", bin_ranges)

    def assess_uniformity(self, initialization: bool = False):
        # with 10 bins, each bin width is 2*np.pi/10, so the probability of each bin
        # is 0.1/(2*np.pi/10)
        self.velocity_angles.append(
            np.arctan2(self.left_particles[0].vy, self.left_particles[0].vx)
        )
        self.bin_velocities(
            velocities=self.velocity_angles,
            bin_count=10,
            prefix="angle",
            initialization=initialization,
            normalize=False,
        )
        # chi2_statistic, p_value = chi_square_test(self.angle_velocities_bins)
        _, pval_chi = stat_signif.chi_square_test(self.angle_velocities_bins)
        _, pval_chi_rel = stat_signif.chi_square_relaxed(self.angle_velocities_bins)
        _, pval_ks = stat_signif.kolmogorov_smirnov_uniform_test(
            self.angle_velocities_bins
        )
        self.unifpVals["chi"].append(pval_chi)
        self.unifpVals["chi-rel"].append(pval_chi_rel)
        self.unifpVals["ks"].append(pval_ks)

    def find_equipartition_temperature(self):
        self.elementToSpeed = {self.left_atom: [], self.right_atom: []}
        elementToSum = {self.left_atom: 0, self.right_atom: 0}
        for particle in self.left_particles:
            self.elementToSpeed[self.left_atom].append(
                np.sqrt(particle.vx**2 + particle.vy**2)
            )
            elementToSum[self.left_atom] += particle.vx**2 + particle.vy**2
        for particle in self.right_particles:
            self.elementToSpeed[self.right_atom].append(
                np.sqrt(particle.vx**2 + particle.vy**2)
            )
            elementToSum[self.right_atom] += particle.vx**2 + particle.vy**2
        maxKe = float("inf")
        for atom, count, speed_sum in [
            (self.left_atom, self.num_left, elementToSum[self.left_atom]),
            (self.right_atom, self.num_right, elementToSum[self.right_atom]),
        ]:
            mass_speed = cnst.ATOMS_LIBRARY[atom]["mass"] * speed_sum
            maxKe = min(maxKe, 0.5 * mass_speed)
            self.elementToT["equipartition"].setdefault(atom, []).append(
                cnst.TEMP_CONVERSION_FACTOR / (3 * cnst.R * 1000) * mass_speed / count
            )
        if self.rigid_wall:
            self.energy_wall.energy_limit = 0.05 * maxKe

    def update_v_mp_freq(self):
        max_bins = max(
            max(self.abs_left_velocities_bins), max(self.abs_right_velocities_bins)
        )
        new_val = min(max_bins, 2) * 1.2
        if np.abs(new_val - self.v_mp_freq) > 0.3:
            self.v_mp_freq = new_val

    def export_statistics(self):
        perc = lambda x: "{:.2f}%".format(x * 100)
        data = {
            "left_fraction": self.left_fractions[-1],
            "right_fraction": self.right_fractions[-1],
            "abs_left_velocities_bins": self.abs_left_velocities_bins,
            "abs_left_velocities_bin_ranges": self.abs_left_velocities_bin_ranges,
            "abs_right_velocities_bins": self.abs_right_velocities_bins,
            "abs_right_velocities_bin_ranges": self.abs_right_velocities_bin_ranges,
            "angle_velocities_bins": self.angle_velocities_bins,
            "angle_velocities_bin_ranges": self.angle_velocities_bin_ranges,
            "unif_pval_ks": perc(self.unifpVals["ks"][-1]),
            "unif_pval_chi": perc(self.unifpVals["chi"][-1]),
            "unif_pval_chi_rel": perc(self.unifpVals["chi-rel"][-1]),
            "min_temp": self.min_temp,
            "max_temp": self.max_temp,
            "v_mp_freq": self.v_mp_freq,
            **self.particlesStyle,
        }
        for element, t in self.elementToT["equipartition"].items():
            data[f"{self.elToDir[element]}_equip_temperature"] = "{:.2f}".format(
                np.round(t[-1], 2)
            )
        return data

    def export_particles(self):
        data = {
            "left_particles": [p.render() for p in self.left_particles],
            "right_particles": [p.render() for p in self.right_particles],
            "update_frequency": self.update_frequency,
            **self.particlesStyle,
        }
        return data

    def analyze_game(self, fname: Optional[str] = None):
        if fname is None:
            fname = get_timestamp()
        init_temp = self.init_params["left_temperature"]
        figs = FigureMaker()
        figs.create_fractions_scatter_plot(
            self.left_fractions, self.right_fractions, init_temp, fname
        )
        figs.create_equipartition_scatter_plot(self.elementToT["equipartition"], init_temp, fname)
        figs.create_pval_scatter_plot(self.unifpVals.values(), self.angle_velocities_bins, self.angle_velocities_bin_ranges, init_temp, fname)
        figs.create_speed_distribution_plot(
            self.abs_left_velocities_bins,
            self.abs_right_velocities_bins,
            self.abs_left_velocities_bin_ranges,
            self.abs_right_velocities_bin_ranges,
            self.particlesStyle["left_color"],
            self.particlesStyle["right_color"],
            self.particlesStyle["left_name"],
            self.particlesStyle["right_name"],
            self.elementToT["equipartition"],
            self.time,
            fname,
        )

if __name__ == "__main__":
    # game = Game(200)
    # for _ in tqdm(range(10_000)):
    #     game.update()
    # game.analyze_game()
    # print(game.export())

    pass
