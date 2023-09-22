import functools as _functools

import  pygame as _pygame


class _UIElement:
    """Base class for ui elements"""
    def __init__(self, width, height, x, y):
        self.rect = _pygame.Rect(x, y, width, height)

        self.WIDTH = width
        self.HEIGHT = height
        self.x = x
        self.y = y

class Graph:
    def __init__(self, size, increment):
        self.size = size
        self.increment = increment
        self.graph = _pygame.Surface((size, size))

        self.reset()

    def reset(self):
        self.graph.fill((255, 255, 255))

        for length in range(self.size // self.increment + 1):
            _pygame.draw.line(self.graph, (0, 0, 0), (0, length * self.increment), (self.size, length * self.increment))
            _pygame.draw.line(self.graph, (0, 0, 0), (length * self.increment, 0), (length * self.increment, self.size))


    def plot(self, points, show_points=False):
        self.reset()
        if show_points:
            for point in points:
                x, y = point
                y = self.size - y

                _pygame.draw.circle(self.graph, (0, 0, 0), (x, y), 5)

        _pygame.draw.lines(self.graph, (0, 0, 0), False, points, width=5)


    def plot_y(self, points, show_points=False):
        self.reset()
        line_points = []

        for i, point in enumerate(points):
            x, y = i * self.increment, self.size - point
            line_points.append((x, y))

            if show_points:
                _pygame.draw.circle(self.graph, (0, 0, 0), (x, y), 5)

        _pygame.draw.lines(self.graph, (0, 0, 0), False, line_points, width=5)


    def draw(self, surface, x, y):
        surface.blit(self.graph, (x, y))


class Button(_UIElement):
    def __init__(self, button_up_image: _pygame.Surface, button_down_image: _pygame.Surface, x: int, y: int):
        self.button_up_image = button_up_image
        self.button_down_image = button_down_image
        self.current_image = self.button_up_image

        super().__init__(*self.button_up_image.get_size(), x, y)


    def get_pressed(self, x, y, mouse_button=0):
        if _pygame.mouse.get_pressed(5)[mouse_button] and self.rect.collidepoint(x, y):
            self.current_image = self.button_down_image
            return True

        self.current_image = self.button_up_image
        return False


    def draw(self, surface):
        _pygame.draw.rect(surface, (255, 255, 255), self.rect)
        surface.blit(self.current_image, (self.x, self.y))


    def reset(self):
        self.__init__(self.button_up_image, self.button_down_image, self.x, self.y)


class ToggleButton(Button):
    def __init__(self, button_up_image: _pygame.Surface, button_down_image: _pygame.Surface, x: int, y: int):
        super().__init__(button_up_image, button_down_image, x, y)
        self.pressed = False

    def get_pressed(self, x, y, mouse_button=0):
        if _pygame.mouse.get_pressed(5)[mouse_button] and self.rect.collidepoint(x, y):
            self.current_image = self.button_up_image if self.pressed else self.button_down_image
            self.pressed = not self.pressed

        return self.pressed


class Slider(_UIElement):
    def __init__(self, slider_image, bar_image, x, y, direction="horizontal"):
        self.slider_image = slider_image
        self.bar_image = bar_image

        super().__init__(*self.bar_image.get_size(), x, y)


        self.direction = direction

        if self.direction == "horizontal":
            self.MAXIMUM = self.x + self.WIDTH - self.slider_image.get_width()
            self.MINIMUM = self.x 

            self.slider_x = self.MINIMUM
            self.slider_y = self.y

        else:
            self.MAXIMUM = self.y + self.HEIGHT - self.slider_image.get_height()
            self.MINIMUM = self.y

            self.slider_y = self.MINIMUM
            self.slider_x = self.x

        self.previous_distance = 0


    def move(self, x, y, mouse_button=0):
        if self.rect.collidepoint(x, y) and _pygame.mouse.get_pressed(5)[mouse_button]:
            x -= self.slider_image.get_width() / 2
            y -= self.slider_image.get_height() / 2

            if self.direction == "horizontal":
                if self.MINIMUM < x and x < self.MAXIMUM:
                    self.slider_x = x

            elif self.MINIMUM < y and y < self.MAXIMUM:
                    self.slider_y = y

    def get_distance(self):
        if self.direction == "horizontal":
            self.previous_distance = (self.slider_x - self.x) / self.WIDTH

        else:
            self.previous_distance = (self.slider_y - self.y) / self.HEIGHT

        return self.previous_distance


    def get_rel(self, x, y, mouse_button=0):
        if self.rect.collidepoint(x, y) and _pygame.mouse.get_pressed(5)[mouse_button]:
            if self.direction == "horizontal" and self.MINIMUM < x and x < self.MAXIMUM:
                return _pygame.mouse.get_rel()[1]

            elif self.MINIMUM < y and y < self.MAXIMUM:
                return _pygame.mouse.get_rel()[1]

        return 0.0


    def draw(self, surface):
        _pygame.draw.rect(surface, (255, 255, 255), self.rect)
        surface.blit(self.bar_image, (self.x, self.y))
        surface.blit(self.slider_image, (self.slider_x, self.slider_y))


    def reset(self):
        self.__init__(self.slider_image, self.bar_image, self.x, self.y, self.direction)


class TextInputArea(_UIElement):
    def __init__(self, image, font, x, y, bourder_size=0):
        self.font = font
        self.image = image

        super().__init__(*self.image.get_size(), x, y)

        self.bourder_size = bourder_size

        self.border_x = [
            self.x + bourder_size,
            self.x + self.HEIGHT - bourder_size
        ]


        self.border_y = [
            self.y + bourder_size,
            self.y + self.WIDTH - bourder_size
        ]

        self.text = "0"

        self.is_selected = False


    def get_selected(self, x, y):
        if _pygame.mouse.get_pressed(5)[0]:
            if self.rect.collidepoint(x, y):

                self.is_selected = True

            else:
                self.is_selected = False

        return self.is_selected


    def handle_event(self, event):
        if self.is_selected:
            if event.key == _pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            else:
                self.text += event.unicode
                if self.font.render(self.text, True, (255, 0, 0)).get_width() > self.image.get_width() - self.bourder_size:
                    self.text = self.text[:-1]

            self.text = self.filter_num(self.text, 255)

            return self.text

    def filter_num(self, text, max):
        if text.isdigit():
            if int(text) > max:
                return str(int(text[:-1]))

            return str(int(text))

        text = ''.join(i for i in text if i.isdigit())

        return text if text else "0"



    def draw(self, surface, colour):
        text_surface = self.font.render(self.text, True, colour)
        surface.blit(self.image, (self.x, self.y))
        surface.blit(text_surface, (self.border_x[0], self.y))

class ColourPicker(_UIElement):
    def __init__(self, width, height, x, y):
        super().__init__(width, height, x, y)

        self.surface = _pygame.Surface((self.WIDTH, self.HEIGHT)).convert()
        self.current_rgb = [255, 0, 0]
        self.current_rgb_num = 1
        self.increase = True


    @_functools.lru_cache(maxsize=None)
    def decrease_brightness(self, rgb, amount):
        return tuple(x * (1 - amount) for x in rgb)

    @_functools.lru_cache(maxsize=None)
    def _rgb_to_hsl(self, red, green, blue):
        red, green, blue = red / 255.0, green / 255.0, blue / 255.0
        max_channel = max(red, green, blue)
        min_channel = min(red, green, blue)
        lightness = (max_channel + min_channel) / 2

        if max_channel == min_channel:
            hue = saturation = 0
        else:
            channel_difference = max_channel - min_channel
            saturation = (channel_difference / (2 - max_channel - min_channel)
                        if lightness > 0.5 else channel_difference / (max_channel + min_channel))

            if max_channel == red:
                hue = (green - blue) / channel_difference + (6 if green < blue else 0)
            elif max_channel == green:
                hue = (blue - red) / channel_difference + 2
            else:
                hue = (red - green) / channel_difference + 4

            hue /= 6

        return hue, saturation, lightness

    @_functools.lru_cache(maxsize=None)
    def _hue_to_rgb(self, p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p

    @_functools.lru_cache(maxsize=None)
    def _hsl_to_rgb(self, hue, saturation, lightness):
        if saturation == 0:
            red = green = blue = lightness
        else:
            q = lightness * (1 + saturation) if lightness < 0.5 else lightness + saturation - lightness * saturation
            p = 2 * lightness - q
            red = self._hue_to_rgb(p, q, hue + 1/3)
            green = self._hue_to_rgb(p, q, hue)
            blue = self._hue_to_rgb(p, q, hue - 1/3)

        return round(red * 255), round(green * 255), round(blue * 255)

    @_functools.lru_cache(maxsize=None)
    def decrease_saturation(self, rgb, amount):
        hue, saturation, lightness = self._rgb_to_hsl(*rgb)
        new_saturation = max(0, saturation - amount)
        new_rgb = self._hsl_to_rgb(hue, new_saturation, lightness)
        return new_rgb

    def create(self, start_colour):
        start_colour = tuple(start_colour)
        for i in range(self.WIDTH):

            colour = self.decrease_saturation(start_colour, (i / self.WIDTH))
            for j in range(self.HEIGHT):
                colour = self.decrease_brightness(colour, (j / self.HEIGHT/ 30))
                self.surface.set_at((i, j), colour)


    def update(self, offset=0):
        if offset:
            colour_index = self.current_rgb_num % 3

            self.current_rgb[colour_index] += (offset if self.increase else -offset)
            current_colour = self.current_rgb[colour_index]

            if current_colour >= 255 or current_colour <= 0:
                self.current_rgb[colour_index] = 255 if self.increase else 0

                if self.increase:
                    self.current_rgb[colour_index] = 255
                    next_offset = current_colour - 255

                else:
                    self.current_rgb[colour_index] = 0
                    next_offset = abs(current_colour)

                self.increase = not self.increase
                self.current_rgb_num -= offset // abs(offset)

                self.update(next_offset)

        self.create(self.current_rgb)


    def reset(self):
        self.current_rgb = [255, 0, 0]
        self.current_rgb_num = 1
        self.increase = True


    def is_in_bounds(self, x, y):
        return x > 0 + self.x and x < self.WIDTH + self.x and y > 0 + self.y and y < self.HEIGHT + self.y


    def select_colour(self, x, y):
        if self.is_in_bounds(x, y):
            colour = list(self.surface.get_at((x, y)))[:-1]
            return colour

    def draw(self, surface):
        surface.blit(self.surface, (self.x, self.y))