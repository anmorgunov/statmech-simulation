import pytest
import numpy as np
from .Particle import (
    Particle,
    WIDTH,
    HEIGHT,
)


class TestParticle:
    @pytest.mark.parametrize(
        "element, x, y, speed, radius, mass, color, special",
        [
            ("H", 100, 100, 10, 5, 1, "red", False),
            ("He", 10, 10, 0, 10, 2, "blue", True),
            ("Li", WIDTH - 1, HEIGHT - 1, 5, 1, 1, "green", False),
        ],
    )
    def test_init(self, element, x, y, speed, radius, mass, color, special):
        particle = Particle(element, x, y, speed, radius, mass, color, special)
        assert particle.x == x
        assert particle.y == y
        assert particle.element == element
        assert 0 <= particle.angle < 2 * np.pi
        assert particle.mass == mass
        assert particle.radius == radius
        assert particle.color == color
        assert particle.special is special

    def test_move_within_boundaries(self):
        particle = Particle("H", 400, 250, 10, 5, 1, "red")
        initial_x, initial_y = particle.x, particle.y
        particle.move()
        assert 0 <= particle.x <= WIDTH
        assert 0 <= particle.y <= HEIGHT
        assert not (particle.x == initial_x and particle.y == initial_y)

    def test_reflection_at_boundaries(self):
        for x, y in [(5, 250), (WIDTH - 5, 250), (400, 5), (400, HEIGHT - 5)]:
            particle = Particle("H", x, y, 10, 5, 1, "red")
            initial_vx, initial_vy = particle.vx, particle.vy
            particle.move()
            if particle.x <= particle.radius or particle.x >= WIDTH - particle.radius:
                assert particle.vx == -initial_vx
            if particle.y <= particle.radius or particle.y >= HEIGHT - particle.radius:
                assert particle.vy == -initial_vy

    @pytest.mark.parametrize(
        "x, y",
        [
            (-10, 250),
            (810, 250),
            (400, -10),
            (400, 510),
        ],
    )
    def test_out_of_bounds_initialization(self, x, y):
        with pytest.raises(ValueError):
            Particle("H", x, y, 10, 5, 1, "red")

    @pytest.mark.parametrize(
        "x, y, expected_message",
        [
            (-10, 250, f"x must be between 5 and {WIDTH - 5}"),
            (810, 250, f"x must be between 5 and {WIDTH - 5}"),
            (400, -10, f"y must be between 5 and {HEIGHT - 5}"),
            (400, 510, f"y must be between 5 and {HEIGHT - 5}"),
        ],
    )
    def test_out_of_bounds_initialization(self, x, y, expected_message):
        with pytest.raises(ValueError) as exc_info:
            Particle("H", x, y, 10, 5, 1, "red")
        assert str(exc_info.value) == expected_message

    @pytest.mark.parametrize(
        "initial_speed, radius, mass, expected_message",
        [
            (-1, 5, 1, "Speed must be positive"),
            (10, 0, 1, "Radius must be positive"),
            (10, 5, 0, "Mass must be positive"),
        ],
    )
    def test_invalid_speed_radius_mass(
        self, initial_speed, radius, mass, expected_message
    ):
        with pytest.raises(AssertionError) as exc_info:
            Particle("H", 400, 250, initial_speed, radius, mass, "red")
        assert str(exc_info.value) == expected_message


class TestParticleCollision:
    def create_particle_pair(self, x1, y1, x2, y2, speed1, speed2, radius, mass):
        particle1 = Particle("H", x1, y1, speed1, radius, mass, "red")
        particle2 = Particle("He", x2, y2, speed2, radius, mass, "blue")
        return particle1, particle2

    def test_collision_detection(self):
        radius, mass = 5, 1
        # Test case where particles collide
        p1, p2 = self.create_particle_pair(100, 100, 110, 100, 10, 10, radius, mass)
        p1.check_collision(p2)
        dx, dy = p2.x - p1.x, p2.y - p1.y
        distance = np.sqrt(dx**2 + dy**2)
        assert distance <= radius * 2

        # Test case where particles do not collide
        p1, p2 = self.create_particle_pair(100, 100, 200, 200, 10, 10, radius, mass)
        p1.check_collision(p2)
        dx, dy = p2.x - p1.x, p2.y - p1.y
        distance = np.sqrt(dx**2 + dy**2)
        assert distance > radius * 2

    def test_velocity_update_on_collision(self):
        radius, mass = 5, 1
        p1, p2 = self.create_particle_pair(100, 100, 110, 100, 10, 10, radius, mass)
        initial_v1 = np.array([p1.vx, p1.vy])
        initial_v2 = np.array([p2.vx, p2.vy])

        p1.check_collision(p2)

        # Ensure velocities are updated
        assert not np.array_equal(np.array([p1.vx, p1.vy]), initial_v1)
        assert not np.array_equal(np.array([p2.vx, p2.vy]), initial_v2)

        # Test for conservation of momentum (optional, if relevant)
        total_initial_momentum = mass * initial_v1 + mass * initial_v2
        total_final_momentum = mass * np.array([p1.vx, p1.vy]) + mass * np.array(
            [p2.vx, p2.vy]
        )
        np.testing.assert_almost_equal(total_initial_momentum, total_final_momentum)
        
class TestParticleRendering:
    @pytest.fixture
    def sample_particle(self):
        return Particle("H", 100.0, 200.0, 10.0, 5.0, 1.0, "red")

    def test_render(self, sample_particle):
        rendered_data = sample_particle.render()
        assert rendered_data["x"] == sample_particle.x
        assert rendered_data["y"] == sample_particle.y
        assert rendered_data["color"] == sample_particle.color

    def test_repr(self, sample_particle):
        expected_repr = (
            f"H(100.0, 200.0, {sample_particle.vx:.1f}, {sample_particle.vy:.1f})"
        )
        assert repr(sample_particle) == expected_repr
