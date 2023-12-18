from game import Game, Particle, Grid
import constants
import pytest
import numpy as np


@pytest.fixture
def sample_particle():
    # Create a particle for testing
    return Particle(x=50, y=50, element="He", mass=4.002602)  # Helium for example


def test_move_no_collision(sample_particle):
    # Test movement without any wall collision
    initial_x, initial_y = sample_particle.x, sample_particle.y
    sample_particle.move()

    assert sample_particle.x != initial_x
    assert sample_particle.y != initial_y
    assert 0 < sample_particle.x < constants.WIDTH
    assert 0 < sample_particle.y < constants.HEIGHT


def test_move_collision_with_vertical_wall(sample_particle):
    # Test collision with vertical wall
    sample_particle.x = constants.WIDTH - 1  # Near right wall
    sample_particle.vx = 10  # Moving right
    sample_particle.move()

    assert sample_particle.vx < 0  # Velocity should be reversed
    assert sample_particle.x <= constants.WIDTH  # Particle should not go beyond wall


def test_move_collision_with_horizontal_wall(sample_particle):
    # Test collision with horizontal wall
    sample_particle.y = constants.HEIGHT - 1  # Near top wall
    sample_particle.vy = 10  # Moving up
    sample_particle.move()

    assert sample_particle.vy < 0  # Velocity should be reversed
    assert sample_particle.y <= constants.HEIGHT  # Particle should not go beyond wall


def test_move_collision_with_corner(sample_particle):
    # Test collision with corner
    sample_particle.x, sample_particle.y = (
        constants.WIDTH - 1,
        constants.HEIGHT - 1,
    )  # Near top-right corner
    sample_particle.vx, sample_particle.vy = 10, 10  # Moving towards corner
    sample_particle.move()

    assert (
        sample_particle.vx < 0 and sample_particle.vy < 0
    )  # Both velocities should be reversed
    assert (
        sample_particle.x <= constants.WIDTH and sample_particle.y <= constants.HEIGHT
    )  # Particle should not go beyond walls


def test_move_high_speed(sample_particle):
    # Test high-speed particle not tunneling through walls
    sample_particle.x, sample_particle.vx = 1, -1000  # High speed towards left wall
    sample_particle.move()

    assert sample_particle.vx > 0  # Velocity should be reversed
    assert 0 <= sample_particle.x  # Particle should not tunnel through wall


@pytest.fixture
def particle_setup():
    # Setup for particles, adjust as needed
    return Particle(x=1, y=1, element="He", mass=4.002602), Particle(
        x=20, y=20, element="He", mass=4.002602
    )

def test_no_collision(particle_setup):
    p1, p2 = particle_setup
    p1.check_collision(p2)
    assert np.sqrt(p1.vx**2 + p1.vy**2) == np.sqrt(
        p2.vx**2 + p2.vy**2
    )  # No change in speed


def test_head_on_collision(particle_setup):
    p1, p2 = particle_setup
    p1.x, p1.y = 2, 1
    p2.x, p2.y = 3, 1
    p1.vx, p1.vy = 1, 0
    p2.vx, p2.vy = -1, 0
    p1.check_collision(p2)
    assert p1.vx == -1 and p2.vx == 1  # Velocity reversed


def test_glancing_collision(particle_setup):
    p1, p2 = particle_setup
    p1.x, p1.y = 2.5, 1
    p2.x, p2.y = 2.5, 2
    p1.vx, p1.vy = 0, 1
    p2.vx, p2.vy = 0, -1
    p1.check_collision(p2)
    assert p1.vy < 0 and p2.vy > 0  # Velocity direction changed


def test_edge_case_collision(particle_setup):
    p1, p2 = particle_setup
    p1.x, p1.y = 2.9, 1
    p2.x, p2.y = 3.1, 1
    p1.vx, p1.vy = 10, 0
    p2.vx, p2.vy = -10, 0
    p1.check_collision(p2)
    assert p1.vx < 0 and p2.vx > 0  # Large velocity change


def test_static_collision(particle_setup):
    p1, p2 = particle_setup
    p1.x, p1.y = 2, 1
    p2.x, p2.y = 3, 1
    p1.vx, p1.vy = 1, 0
    p2.vx, p2.vy = 0, 0
    p1.check_collision(p2)
    assert p1.vx < 1 and p2.vx > 0  # Momentum transfer


# Run the tests
# pytest test_particle_collision.py
