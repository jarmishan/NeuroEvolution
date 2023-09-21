import sys
import time
import math

import pygame
import numpy

from enviroment import DrawingEnvironment, Track
from population import Population
from gui import Graph

pygame.init()
numpy.random.seed(0)

WIDTH = 1400
HEIGHT = 900
FPS = 60
prev_time = 0

clock = pygame.time.Clock()
win = pygame.display.set_mode((WIDTH, HEIGHT))
paint = DrawingEnvironment(WIDTH, HEIGHT)

font = pygame.font.Font("NeuroEvoloution/assets/pixel_font.ttf", 45)
title = pygame.image.load("NeuroEvoloution/assets/title.png").convert_alpha()
start_button = pygame.image.load("NeuroEvoloution/assets/start.png").convert_alpha()

start_button.set_colorkey((255, 60, 60))
prev_time = time.time()
train = False
start = False

while True:
    win.fill((255, 255, 255))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    current_time = time.time() 

    dt = (current_time - prev_time) * FPS
    prev_time = current_time

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        
        if start:
            if event.type == pygame.MOUSEBUTTONDOWN:
                paint.update_toggle_buttons()

            if event.type == pygame.KEYDOWN:
                paint.update_text_boxes(event)

            if event.type == pygame.MOUSEWHEEL:
                paint.update_car(event)


    if not start:
        win.fill((85, 85, 85))
        win.blit(title, (50, 10))
        win.blit(start_button, (359, 475))

        if any(keys) or any(pygame.mouse.get_pressed(5)):
            start = True


    elif not paint.saved:
        paint.update(win)
        pygame.draw.circle(win, (paint.colour), (mouse_x, mouse_y), paint.pen_size // 2, width=1)
        paint.draw_ui(win)
        
        
    elif not train:
        track = Track(paint.canvas)

        population = Population(
            250, 
            track,  
            paint.car_position, 
            paint.car_angle*math.pi/180
        )

        train = True
        

    if train:
        increment = paint.BORDER_SIZE // (population.generation)
        graph = Graph(paint.BORDER_SIZE + 1, increment)
        points = [0] + population.history

        if len(points) > 1:
            graph.plot_y([point * (graph.size / max(population.history)) for point in points])

        track.draw(win, 0, 0)
        population.train(win, dt)

        data = [
            font.render(f"generation: {population.generation} ", True, (255, 255, 255)),
            font.render(f"population: {len(population.cars)}/{population.population_size}", True, (255, 255, 255)),
            font.render(f"best fitness: {round(population.best_fitness, 2)}", True, (255, 255, 255)),
            font.render(f"best current fitness: {round(population.best_current_fitness, 2)} ", True, (255, 255, 255)),          
        ]

        for i, datum in enumerate(data):
            win.blit(datum, (10, i * 35))

        graph.draw(win, WIDTH - graph.size, 0)

    clock.tick(FPS) 
    
    pygame.display.flip()