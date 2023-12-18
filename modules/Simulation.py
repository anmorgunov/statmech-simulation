import numpy as np
import constants
from scipy.optimize import curve_fit
from tqdm import tqdm
from typing import Optional, List, Tuple

from .Figures import FigureMaker
from .Particle import Particle
from .Grid import Grid
from .Quadtree import QuadtreeNode
from .utils import phys_constants as cnst
from .utils import significance as stat_signif

WIDTH = 800
HEIGHT = 500


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
    ):
        # self.particles = []
        min_mass = min(
            cnst.ATOMS_LIBRARY[atom]["mass"] for atom in [left_atom, right_atom]
        )
        self.min_temp = min(left_temperature, right_temperature)
        self.max_temp = max(left_temperature, right_temperature)
        v_mp_freq = cnst.most_probable_freq(self.max_temp, min_mass)
        self.init_params = {
            "num_left": num_left,
            "left_atom": left_atom,
            "num_right": num_right,
            "right_atom": right_atom,
            "left_temperature": left_temperature,
            "right_temperature": right_temperature,
            "use_quadtree": use_quadtree,
            "update_frequency": update_frequency,
        }
        self.v_mp_freq = v_mp_freq
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
        self.velocity_angles = []
        self.update_compartment_fractions()
        self.compute_velocity_distribution(initialization=True)
        self.find_equipartition_temperature()
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
            # for particle_i in self.particles:
            #     for particle_j in self.particles:
            #         if particle_i is not particle_j:
            #             particle_i.check_collision(particle_j)

        if self.time % self.update_frequency == 0:
            self.update_compartment_fractions()
            self.compute_velocity_distribution()
            self.find_equipartition_temperature()
            self.assess_uniformity()
            self.time = 0
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

    def compute_velocity_distribution(self, initialization: bool = False):
        self.abs_velocities = [np.sqrt(p.vx**2 + p.vy**2) for p in self.particles]
        # self.velocity_angles = [np.arctan2(p.vy, p.vx) for p in self.particles]
        # self.x_velocities = [p.vx**2 for p in self.particles]
        # self.y_velocities = [p.vy**2 for p in self.particles]

        for prefix, data in [
            ("abs", self.abs_velocities),
            # ("x", self.x_velocities),
            # ("y", self.y_velocities),
        ]:
            self.bin_velocities(
                velocities=data,
                bin_count=10,
                prefix=prefix,
                initialization=initialization,
            )

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
        self.unif_pval_ks = f"{(pval_ks)*100:.2f}%"
        self.unif_pval_chi = f"{(pval_chi)*100:.2f}%"
        self.unif_pval_chi_rel = f"{(pval_chi_rel)*100:.2f}%"

    def bin_velocities(
        self, velocities, bin_count, prefix, initialization=False, normalize=True
    ):
        if initialization:
            bins = np.array([0] * bin_count)
            bins[bin_count // 2] = len(velocities)  # Put all counts in the middle bin
            value = velocities[0]
            bin_ranges = [(value, value) for _ in range(bin_count)]
        else:
            bins, edges = np.histogram(velocities, bins=bin_count, density=normalize)
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

    def export_statistics(self):
        data = {
            "left_fraction": self.left_fractions[-1],
            "right_fraction": self.right_fractions[-1],
            "abs_velocities_bins": self.abs_velocities_bins,
            "abs_velocities_bin_ranges": self.abs_velocities_bin_ranges,
            "angle_velocities_bins": self.angle_velocities_bins,
            "angle_velocities_bin_ranges": self.angle_velocities_bin_ranges,
            # "uniformity_confidence": self.uniformity_confidence,
            "unif_pval_ks": self.unif_pval_ks,
            "unif_pval_chi": self.unif_pval_chi,
            "unif_pval_chi_rel": self.unif_pval_chi_rel,
            # "x_velocities_bins": self.x_velocities_bins,
            # "x_velocities_bin_ranges": self.x_velocities_bin_ranges,
            # "y_velocities_bins": self.y_velocities_bins,
            # "y_velocities_bin_ranges": self.y_velocities_bin_ranges,
            "min_temp": self.min_temp,
            "max_temp": self.max_temp,
            "v_mp_freq": self.v_mp_freq,
        }
        for element, t in self.elementToT["equipartition"].items():
            data[f"{element.lower()}_equipartition_temperature"] = "{:.2f}".format(
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
