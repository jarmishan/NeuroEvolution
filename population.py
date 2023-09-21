import math as _math

import numpy as _numpy
import pygame as _pygame

from neuralnetwork import NeuroEvoloution, Dense


class Car:
    def __init__(self, track, start_position, start_angle):
        self.image = _pygame.image.load("NeuroEvoloution/assets/car.png").convert_alpha()
        self.rotated_image = self.image
        self.track = track

        self.width, self.height = self.rotated_image.get_size()
        self.starting_position = start_position
        self.x, self.y = self.starting_position
        self.angle = start_angle
        self.velocity = 0

        self.MAX_VELOCITY = 12
        self.ACCELERATION = 0.3
        self.FRICTION = 0.2
        
        self.DIRECTIONS = 32
        self.STEP_ANGLE = 360 / self.DIRECTIONS * _math.pi / 180
        self.MAX_DEPTH = 500

        self.brain = NeuroEvoloution(
            Dense(self.DIRECTIONS, 24, "tanh"),
            Dense(24, 16, "tanh"),
            Dense(16, 12, "tanh"),
            Dense(12, 8, "tanh"),
            Dense(8, 5, "tanh"),
        )
        
        self.fitness = 0
        self.num_frames = 0

    @property
    def has_collided(self):
        car_mask = _pygame.mask.from_surface(self.rotated_image)
        return car_mask.overlap(self.track.mask, (-self.x, -self.y)) or self.x < 0 or self.x > self.track.WIDTH or self.y < 0 or self.y > self.track.HEIGHT
    
    @property
    def in_bounds(self):
        return 0 < self.x < self.track.WIDTH and 150 < self.y < self.track.HEIGHT
    
    def update_fitness(self):
        self.fitness += _math.sqrt((self.prev_x - self.x) ** 2 + (self.prev_y - self.y) ** 2)

    def get_stationary_frames(self):
        return int(not (abs(self.prev_x - self.x) > 2))


    def convert(self, inputs):
        return _numpy.array([inputs[i][0] for i in range(2)]),  _numpy.array([inputs[i+2][0] for i in range(3)])
    

    def get_state(self):
        inputs = _numpy.zeros(self.DIRECTIONS)
        start_angle = self.angle

        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        for direction in range(self.DIRECTIONS):
            angle_x = _math.sin(start_angle)
            angle_y = _math.cos(start_angle)

            for depth in range(0, self.MAX_DEPTH, 5):
                target_x = center_x - angle_x * depth
                target_y = center_y + angle_y * depth

                try:
                    if self.track.mask.get_at((target_x, target_y)):
                        inputs[direction] = 1 - depth / self.MAX_DEPTH
                        break

                except IndexError:
                    inputs[direction] = 0
                    break

            start_angle += self.STEP_ANGLE

        return _numpy.reshape(inputs, (self.DIRECTIONS, 1))
    
    
    def ai_move(self):
        actions = [
            ["forward", "backward"],
            ["left", "right", None]
        ]

        inputs = self.get_state()
        outputs = self.convert(self.brain.forward_propogation(inputs))

        return [
            actions[0][outputs[0].argmax()],
            actions[1][outputs[1].argmax()]  
        ]


    def change_angle(self, direction, dt):
        delta_angle = (self.velocity / 100) * dt

        if direction == "left":
            self.angle -= delta_angle
            
        elif direction == "right":
            self.angle += delta_angle
        

    def move(self, directions, dt):
        self.prev_x = self.x
        self.prev_y = self.y
        if abs(self.velocity) > self.MAX_VELOCITY:
            self.velocity = self.velocity // abs(self.velocity) * self.MAX_VELOCITY

        elif directions[0] == "forward":
            self.velocity -= self.ACCELERATION 
            
        elif directions[0] == "back":
            self.velocity += self.ACCELERATION
            self.fitness -= 100


        if self.velocity:
            self.velocity -= self.velocity // abs(self.velocity) * self.FRICTION
            self.change_angle(directions[1], dt)

        self.velocity = round(self.velocity, 2)

        self.x += _math.sin(self.angle) * self.velocity * dt
        self.y += _math.cos(self.angle) * self.velocity * dt
        
        
    def draw(self,surface):
        angle = self.angle * 180 / _math.pi
        self.rotated_image = _pygame.transform.rotate(self.image, angle)
        surface.blit(self.rotated_image, (self.x, self.y))


    def update(self, surface, dt):
        self.width, self.height = self.rotated_image.get_size()
        self.move(
            self.ai_move(), dt
        )
        self.draw(surface)
        self.update_fitness()
        self.num_frames += self.get_stationary_frames()


class Population:
    def __init__(self, population_size, track, start_position, start_angle=3*_math.pi/2):
        self.population_size = population_size
        self.car_data = track, start_position, start_angle

        self.cars = [Car(*self.car_data) for _ in range(self.population_size)]

        self.generation = 1
        self.best_fitness = -float('inf')
        self.best_current_fitness = -float('inf')
        self.history = []
        

    def load_cars(self):
        for car_index, car in enumerate(self.cars):
            car.brain.load("NeuroEvoloution/models/model")
            if car_index != 0:
                car.brain.mutate(0.3)


    def mutate_cars(self):
        self.generation += 1
        self.cars = [Car(*self.car_data) for _ in range(self.population_size-1)]
        self.best_current_fitness = -float('inf')
    
        self.load_cars()
        self.cars.append(Car(*self.car_data))


    def update_best_genotype(self, car):
        self.best_fitness = car.fitness
        car.brain.save("NeuroEvoloution/models/model")


    def train(self, surface, dt):
        for car in self.cars:
            car.update(surface, dt)

            if car.fitness > self.best_current_fitness:
                self.best_current_fitness = car.fitness
                car.image.set_alpha(255)

                if car.fitness > self.best_fitness:
                    self.update_best_genotype(car)

            else:
                car.image.set_alpha(50)

            if car.has_collided or not car.in_bounds or car.num_frames > 75:
                self.cars.remove(car)


        if not self.cars:
            self.history.append(self.best_current_fitness)
            self.mutate_cars()