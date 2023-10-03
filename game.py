import numpy as np 
import constants

class Particle:
    def __init__(self, x:float, y:float, element:str):
        self.x = x
        self.y = y
        self.element = element
        self.angle = 2 * np.pi * np.random.rand()  # Random direction
        self.vx = constants.BASE_SPEED * np.cos(self.angle)
        self.vy = constants.BASE_SPEED * np.sin(self.angle)

    def move(self):
        # Update position based on velocity
        self.x += self.vx
        self.y += self.vy

        # Boundary checks and reflection for walls
        if self.x <= constants.PARTICLE_RADIUS or self.x >= constants.WIDTH - constants.PARTICLE_RADIUS:
            self.vx = -self.vx
        if self.y <= constants.PARTICLE_RADIUS or self.y >= constants.HEIGHT - constants.PARTICLE_RADIUS:
            self.vy = -self.vy

    def check_collisions(self, other):
        # Check collision with another particle
        dx = self.x - other.x
        dy = self.y - other.y
        distance = np.sqrt(dx**2 + dy**2)
        if distance < 2 * constants.PARTICLE_RADIUS:
            # Reflect velocities
            self.vx, other.vx = other.vx, self.vx
            self.vy, other.vy = other.vy, self.vy

    def render(self):
        return {
            'x': self.x,
            'y': self.y,
            'color': constants.ATOM_TO_COLOR[self.element]
        }

class Game:
    def __init__(self, num_particles):
        
        self.particles = []
        self.atomToCount = {}
        x_high_offset = constants.PARTICLE_RADIUS
        y_low_offset = constants.PARTICLE_RADIUS
        y_high_offset = constants.PARTICLE_RADIUS
        for _ in range(num_particles):
            if np.random.rand(1) < 0.5:
                x_low_offset = constants.WIDTH//2 + constants.PARTICLE_RADIUS
                element = "O"
            else:
                x_low_offset = constants.PARTICLE_RADIUS
                element = "C"
            self.atomToCount[element] = self.atomToCount.get(element, 0) + 1
            x = np.random.randint(x_low_offset, x_high_offset+constants.WIDTH)
            y = np.random.randint(y_low_offset, y_high_offset+constants.HEIGHT)
            self.particles.append(Particle(x=x, y=y, element=element))
        print(self.atomToCount)

    def reset(self):
        self.__init__(len(self.particles))

    def update(self):
        for particle in self.particles:
            particle.move()

        # Collision resolution
        for i in range(len(self.particles)):
            for j in range(i+1, len(self.particles)):
                self.particles[i].check_collisions(self.particles[j])

    def export(self):
        return {
            'particles': [p.render() for p in self.particles]
        }