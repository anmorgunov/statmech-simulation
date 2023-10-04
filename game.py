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
        self.mass = 1

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
            'x': self.x,
            'y': self.y,
            'color': constants.ATOMS_LIBRARY["color"][self.element],
            # "element": self.element
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
        print("Initialized the following atom counts: ", self.atomToCount)
        self.left_fractions = []
        self.right_fractions = []
        self.time = 0
        self.l_dic = []
        self.r_dic = []
        self.update_compartment_fractions()

    def reset(self):
        self.__init__(len(self.particles))


    def update_compartment_fractions(self):
        left_count = sum(1 for p in self.particles if p.x < constants.WIDTH / 2 and p.element == "O")
        right_count = sum(1 for p in self.particles if p.x >= constants.WIDTH / 2 and p.element == "O")
        left_fraction = np.round(100*left_count / (left_count + right_count), 2)
        right_fraction = np.round(100*right_count / (left_count + right_count), 2)
        self.left_fractions.append(left_fraction)
        self.right_fractions.append(right_fraction)
        self.l_dic.append(dict(x=self.time, y=left_fraction))
        self.r_dic.append(dict(x=self.time, y=right_fraction))



    def update(self):
        self.time += 1
        for particle in self.particles:
            particle.move()

        # Collision resolution
        for i in range(len(self.particles)):
            for j in range(i+1, len(self.particles)):
                self.particles[i].check_collisions(self.particles[j])
        self.update_compartment_fractions()

    def export(self):
        return {
            'particles': [p.render() for p in self.particles],
            'left_fractions': self.left_fractions,
            'right_fractions': self.right_fractions,
            'l_dic': self.l_dic,
            'r_dic': self.r_dic,
        }