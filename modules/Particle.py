import numpy as np
from .EnergyWall import EnergyWall

WIDTH = 800
HEIGHT = 500


class Particle:
    def __init__(
        self,
        element: str,
        x: float,
        y: float,
        initial_speed: float,
        radius: float,
        mass: float,
        color: str,
        special: bool = False,
    ):
        if x < radius or x > WIDTH - radius:
            raise ValueError(f"x must be between {radius} and {WIDTH - radius}")
        if y < radius or y > HEIGHT - radius:
            raise ValueError(f"y must be between {radius} and {HEIGHT - radius}")
        assert initial_speed >= 0, "Speed must be positive"
        assert radius > 0, "Radius must be positive"
        assert mass > 0, "Mass must be positive"

        self.x = x
        self.y = y
        self.element = element
        self.angle = 2 * np.pi * np.random.uniform(0, 1)  # Random direction
        self.vx = initial_speed * np.cos(self.angle)
        self.vy = initial_speed * np.sin(self.angle)
        self.mass = mass
        self.radius = radius
        self.color = color
        self.special = special

    def check_wall_collision(self, wall:EnergyWall): 
        """
        Check for collision with the energy wall and update velocities.
        """
        if self.x - self.radius <= wall.position <= self.x + self.radius:
            wall.interact_with_particle(self)
            # adjust position to avoid tunneling
            if self.x < wall.position:
                self.x = wall.position - self.radius
            else:
                self.x = wall.position + self.radius


    def move(self):
        # Update position based on velocity
        self.x += self.vx
        self.y += self.vy

        # Boundary checks and reflection for walls
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.vx = -self.vx
            self.x = max(min(self.x, WIDTH), 0)
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.vy = -self.vy
            self.y = max(min(self.y, HEIGHT), 0)

    def check_collision(self, other):
        # Calculate the distance between the particles
        dx = other.x - self.x
        dy = other.y - self.y
        distance = np.sqrt(dx**2 + dy**2)

        # Check if collision occurs
        if distance <= self.radius + other.radius:
            # Calculate new velocities
            mass_sum = self.mass + other.mass
            v1 = np.array([self.vx, self.vy])
            v2 = np.array([other.vx, other.vy])
            x1 = np.array([self.x, self.y])
            x2 = np.array([other.x, other.y])

            self.vx, self.vy = v1 - 2 * other.mass / mass_sum * np.dot(
                v1 - v2, x1 - x2
            ) / np.linalg.norm(x1 - x2) ** 2 * (x1 - x2)
            other.vx, other.vy = v2 - 2 * self.mass / mass_sum * np.dot(
                v2 - v1, x2 - x1
            ) / np.linalg.norm(x2 - x1) ** 2 * (x2 - x1)

    def render(self):
        return {
            "x": self.x,
            "y": self.y,
            # "color": self.color,
            # "radius": self.radius,
        }

    def __repr__(self):
        return (
            f"{self.element}({self.x:.1f}, {self.y:.1f}, {self.vx:.1f}, {self.vy:.1f})"
        )
