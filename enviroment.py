import math
import os

import cv2
import numpy
import pygame

from gui import TextInputArea, ToggleButton, ColourPicker, Slider, Button
from spritesheet import Spritesheet


class Track:
    def __init__(self, surface, colourkey=(255, 255, 255)):
        track = surface
        self.WIDTH, self.HEIGHT = 1400, 900
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.image.fill((75, 75, 75))
        self.image.blit(track, (0, self.image.get_height() - track.get_height()))
        self.image.set_colorkey(colourkey)
        self.image = self.image.convert_alpha()

        self.mask = pygame.mask.from_surface(self.image)

    @classmethod
    def from_path(cls, path):
        track = pygame.image.load(path)
        return cls(track)


    def draw(self, surface, x, y):

        surface.blit(self.image, (x, y))


class DrawingEnvironment:
    def __init__(self, window_width, window_height):
        spritesheet = Spritesheet("assets/spritesheet.png")
        self.BORDER_SIZE = 150
        self.pen_size = 10

        self.picker = ColourPicker(150, 150, 0, 0)
        self.picker.update()


        rectangle_button = ToggleButton(
            spritesheet.load_sprite("rectangle_up.png"),
            spritesheet.load_sprite("rectangle_down.png"),
            330, 1
        )

        circle_button = ToggleButton(
            spritesheet.load_sprite("circle_up.png"),
            spritesheet.load_sprite("circle_down.png"),
            415, 1
        )

        ellipse_button = ToggleButton(
            spritesheet.load_sprite("ellipses_up.png"),
            spritesheet.load_sprite("ellipses_down.png"),
            500, 1
        )

        rubber_button = ToggleButton(
            spritesheet.load_sprite("rubber_up.png"),
            spritesheet.load_sprite("rubber_down.png"),
            585, 1
        )

        eye_dropper = ToggleButton(
            spritesheet.load_sprite("eyedropper_up.png"),
            spritesheet.load_sprite("eyedropper_down.png"),
            670,
        )

        paint_bucket = ToggleButton(
            spritesheet.load_sprite("paint_bucket_up.png"),
            spritesheet.load_sprite("paint_bucket_down.png"),
            755, 1
        )

        increase = Button(
            spritesheet.load_sprite("add_up.png"),
            spritesheet.load_sprite("add_down.png"),
            840, 1
        )

        decrease = Button(
            spritesheet.load_sprite("subtract_up.png"),
            spritesheet.load_sprite("subtract_down.png"),
            925, 1
        )

        save = Button(
            spritesheet.load_sprite("save_up.png"),
            spritesheet.load_sprite("save_down.png"),
            1010, 1
        )

        load = Button(
            pygame.image.load("assets/load_button_up.png").convert_alpha(),
            pygame.image.load("assets/load_button_down.png").convert_alpha(),
            1095, 1
        )

        car = ToggleButton(
            pygame.image.load("assets/car_button_up.png").convert_alpha(),
            pygame.image.load("assets/car_button_down.png").convert_alpha(),
            1180, 1
        )

        self.buttons = {
            "increase": increase,
            "decrease": decrease,
            "save": save,
            "load": load
        }

        self.toggle_buttons = {
            "rectangle": rectangle_button,
            "circle": circle_button,
            "ellipse": ellipse_button,
            "rubber": rubber_button,
            "eyedropper": eye_dropper,
            "paintbucket": paint_bucket,
            "car": car
        }

        self.tools = {
            "pen": self.line,
            "rectangle": self.rectangle,
            "circle": self.circle,
            "ellipse": self.ellipse,
            "rubber": self.rubber,
            "eyedropper": self.eye_dropper,
            "paintbucket": self.paint_bucket,
            "car": self.car
        }

        self.text_boxes = [
            TextInputArea(
                spritesheet.load_sprite("textbox.png"),
                pygame.font.Font("assets/pixel_font.ttf", 60),
                215, 1+i*49,
                bourder_size=10
            )
            for i in range(3)
        ]


        self.colour_slider = Slider(
            pygame.transform.scale(spritesheet.load_sprite("bar.png"), (46, 10)),
            spritesheet.load_sprite("slider.png"),
            160, 0,
            direction="vertical"
        )

        self.draw_type = "pen"

        self.canvas = pygame.Surface((window_width, window_height - self.BORDER_SIZE))
        self.canvas_x, self.canvas_y = 0, self.BORDER_SIZE
        self.canvas.fill((255, 255, 255))

        self.colour = 0, 0, 0

        self.previous_position = None
        self.start_position = None

        self.shape = pygame.Surface((0, 0))
        self.shape.fill((255, 255, 255))
        self.pos = 0, 0
        self.pressed = False
        self.saved = False

        self.car_position = None
        self.car_angle = 270
        self.car_image = pygame.transform.rotate(pygame.image.load("assets/car.png").convert_alpha(), self.car_angle)

        self.tracks = len(os.listdir("tracks"))
        self.editing_track = None
        self.current_track = 0


    def draw_ui(self, surface):
        pygame.draw.rect(surface, ((75, 75, 75)), (0, 0, self.canvas.get_width(), self.BORDER_SIZE))
        if self.car_position:
            surface.blit(self.car_image, (self.car_position))

        self.picker.draw(surface)
        self.colour_slider.draw(surface)

        for button_type in self.buttons:
            self.buttons[button_type].draw(surface)

        for button_type in self.toggle_buttons:
            self.toggle_buttons[button_type].draw(surface)

        for text_box in self.text_boxes:
            text_box.draw(surface, (75, 75, 75))


    def create_temp_colour(self):
        while True:
            colour = tuple(numpy.random.randint(0, 255) for i in range(3))

            if colour != self.colour:
                return colour


    def line(self, _):
        if self.previous_position:
            pygame.draw.line(self.canvas, self.colour, self.pen_position, self.previous_position, self.pen_size)

            distance = math.sqrt(
                (self.pen_position[0] - self.previous_position[0]) ** 2
                + (self.pen_position[1] - self.previous_position[1]) ** 2
            )

            if distance < 60:
                pygame.draw.circle(self.canvas, self.colour, self.pen_position, self.pen_size / 2.1)

        else:
            pygame.draw.circle(self.canvas, self.colour, self.pen_position, self.pen_size // 2)

        return self.shape, self.pos


    def rectangle(self, surface):
        if not self.start_position:
            self.start_position = self.pen_position

        width, height = self.pen_position[0] - self.start_position[0], self.pen_position[1] - self.start_position[1]

        x, y = self.start_position

        if width < 0:
            x += width
            width = abs(width)

        if height < 0:
            y += height
            height = abs(height)

        rectangle = pygame.Surface((width, height))
        temp_colour = self.create_temp_colour()
        rectangle.fill(temp_colour)
        rectangle.set_colorkey(temp_colour)

        pygame.draw.rect(rectangle, self.colour, (0, 0, width, height), self.pen_size)

        surface.blit(rectangle, (x, y + self.BORDER_SIZE))

        return rectangle, (x, y)


    def rubber(self, _):
        if self.previous_position:
            pygame.draw.line(self.canvas, (255, 255, 255), self.pen_position, self.previous_position, self.pen_size)

            distance = math.sqrt(
                (self.pen_position[0] - self.previous_position[0]) ** 2
                + (self.pen_position[1] - self.previous_position[1]) ** 2
            )

            if distance < 60:
                pygame.draw.circle(self.canvas, (255, 255, 255), self.pen_position, self.pen_size / 2.1)

        else:
            pygame.draw.circle(self.canvas, (255, 255, 255), self.pen_position, self.pen_size // 2)  

        return self.shape, self.pos


    def circle(self, surface):
        if not self.start_position:
            self.start_position = self.pen_position

        x, y = self.start_position
        dx, dy = x - self.pen_position[0], y - self.pen_position[1]

        radius = max(abs(dx), abs(dy)) // 2
        diameter = radius * 2

        if dx > 0:
            x -= diameter

        if dy > 0:
            y -= diameter

        circle = pygame.Surface((diameter, diameter))

        temp_colour = self.create_temp_colour()
        circle.fill(temp_colour)
        circle.set_colorkey(temp_colour)

        pygame.draw.circle(circle, self.colour, (radius, radius), radius, self.pen_size)

        surface.blit(circle, (x, y + self.BORDER_SIZE))

        return circle, (x, y)


    def ellipse(self, surface):
        if not self.start_position:
            self.start_position = self.pen_position

        width, height = self.pen_position[0] - self.start_position[0], self.pen_position[1] - self.start_position[1]

        x, y = self.start_position

        if width < 0:
            x += width
            width = abs(width)

        if height < 0:
            y += height
            height = abs(height)

        temp_colour = self.create_temp_colour()
        ellipse = pygame.Surface((width, height))
        ellipse.fill(temp_colour)
        ellipse.set_colorkey(temp_colour)
        pygame.draw.ellipse(ellipse, self.colour, (0, 0, width, height), width=self.pen_size)

        surface.blit(ellipse, (x, y + self.BORDER_SIZE))

        return ellipse, (x, y)


    def eye_dropper(self, _):
        try:
            self.colour = tuple(list(self.canvas.get_at(self.pen_position))[:3])

            create_colour = (255, 0, 0) if max(self.colour) < 50 else self.colour
            self.picker.create(create_colour)

        except IndexError:
            pass

        return self.shape, self.pos


    def paint_bucket(self, _):
        arr = pygame.surfarray.array3d(self.canvas)
        mask = numpy.zeros((arr.shape[0] + 2, arr.shape[1] + 2), dtype=numpy.uint8)
        point = self.pen_position[1], self.pen_position[0]
        cv2.floodFill(arr, mask, point, self.colour)
        pygame.surfarray.blit_array(self.canvas, arr)

        return self.shape, self.pos


    def car(self, _):
        self.car_position = self.mouse_x, self.mouse_y

        return self.shape, self.pos


    def update_ui(self):
        self.colour_slider.move(self.mouse_x, self.mouse_y)

        for i, text_box in enumerate(self.text_boxes):
            text_box.get_selected(self.mouse_x, self.mouse_y)
            text_box.text = str(self.colour[i])


    def update_toggle_buttons(self):
        self.draw_type = "pen"

        for button_type in self.toggle_buttons:
            if self.toggle_buttons[button_type].get_pressed(self.mouse_x, self.mouse_y):
                self.draw_type = button_type

                for button in self.toggle_buttons:
                    if button != self.draw_type:
                        self.toggle_buttons[button].reset()


    def update_buttons(self):
        if self.buttons["increase"].get_pressed(self.mouse_x, self.mouse_y):
            self.pen_size = min(self.pen_size + 1, 100)

        elif self.buttons["decrease"].get_pressed(self.mouse_x, self.mouse_y):
            self.pen_size = max(self.pen_size - 1, 1)


        elif self.buttons["save"].get_pressed(self.mouse_x, self.mouse_y) and self.car_position:
            if not self.editing_track:
                pygame.image.save(self.canvas, f"tracks/track{self.tracks}.png")

            else:
                pygame.image.save(self.canvas, self.editing_track)
            self.saved = True



        elif self.buttons["load"].get_pressed(self.mouse_x, self.mouse_y) and self.tracks:
            try:
                self.editing_track = f"tracks/track{self.current_track % self.tracks}.png"
                self.canvas = pygame.transform.scale(pygame.image.load(self.editing_track), self.canvas.get_size())
                self.current_track += 1
                pygame.time.delay(100)


            except FileNotFoundError:
                print(f"tracks/track{self.current_track % self.tracks}.png")


    def update_text_boxes(self, event):
        for text_box in self.text_boxes:
            text_box.handle_event(event)

        self.colour = tuple(int(text_box.text) if text_box.text else 0 for text_box in self.text_boxes)

        create_colour = (255, 0, 0) if max(self.colour) < 50 else self.colour
        self.picker.create(create_colour)


    def update_car(self, event):
        if self.draw_type == "car":
            if event.y < 0:
                self.car_angle += 10

            elif event.y > 0:
                self.car_angle -= 10


            self.car_image = pygame.transform.rotate(pygame.image.load("assets/car.png"), self.car_angle).convert_alpha()


    def update_canvas(self, surface):
        if pygame.mouse.get_pressed(5)[0]:
            next_colour = self.picker.select_colour(self.mouse_x, self.mouse_y)

            if next_colour:
                self.colour = next_colour

            if self.mouse_y > self.BORDER_SIZE:
                self.shape, self.pos = self.tools[self.draw_type](surface)

            else:
                surface.blit(self.shape, (self.pos[0], self.pos[1] + self.BORDER_SIZE))

            self.previous_position = self.pen_position
            self.pressed = True


        else:
            if self.pressed:
                self.canvas.blit(self.shape, self.pos)
                self.pressed = True

                self.shape = pygame.Surface((0, 0))
                self.shape.fill((255, 255, 255))
                self.pos = 0, 0

            self.previous_position = None
            self.start_position = None


    def update_picker(self):
        if self.colour_slider.rect.collidepoint(self.mouse_x, self.mouse_y):
            self.picker.reset()
            self.picker.update(int(self.colour_slider.get_distance() * 255 * 6))


    def update(self, surface):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        self.pen_position = self.mouse_x, self.mouse_y - self.BORDER_SIZE
        surface.blit(self.canvas, (self.canvas_x, self.canvas_y))
        self.previous_canvas = self.canvas
        self.update_buttons()
        self.update_picker()
        self.update_canvas(surface)
        self.update_ui()
        self.draw_ui(surface)