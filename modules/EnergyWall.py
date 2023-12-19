from .Particle import Particle
import numpy as np

class EnergyWall:
    def __init__(self, position: float, energy_limit: float = 1e9):
        self.position = position
        self.stored_energy = 0.0
        self.energy_limit = energy_limit
        self.interaction_count = 0
        self.moving_alpha = 0.5
        self.running_average = 0.0

    def interact_with_particle(self, particle: Particle):
        """
        Handle the interaction between the wall and a particle.
        The wall absorbs a fraction of the particle's kinetic energy.
        """
        average_energy = (
            self.running_average
        )  # self.stored_energy / max(self.interaction_count, 1)
        kinetic_energy = 0.5 * particle.mass * (particle.vx**2 + particle.vy**2)
        emit = (
            kinetic_energy < average_energy
            and self.stored_energy >= 0.8 * self.energy_limit
        )
        doTransfer = True
        if emit:
            # Particle has less energy than the average, wall emits energy
            energy_transfer = min(
                np.abs(average_energy - kinetic_energy) * 0.1, self.stored_energy
            )
            self.stored_energy -= energy_transfer
        elif kinetic_energy > average_energy or self.stored_energy < self.energy_limit:
            # Particle has more energy than the average, wall absorbs energy
            self.running_average = (
                self.moving_alpha * kinetic_energy
                + (1 - self.moving_alpha) * self.running_average
            )
            self.interaction_count += 1
            energy_transfer = min(
                (kinetic_energy - average_energy) * 0.1,
                self.energy_limit - self.stored_energy,
            )
            self.stored_energy += energy_transfer
        else:
            doTransfer = False

        if not doTransfer:
            particle.vx *= -1
            return
        new_kinetic_energy = kinetic_energy + (1 if emit else -1) * energy_transfer
        energy_ratio = new_kinetic_energy / kinetic_energy
        particle.vx = -particle.vx * np.sqrt(energy_ratio)  # Reflecting vx
        particle.vy *= np.sqrt(energy_ratio)
