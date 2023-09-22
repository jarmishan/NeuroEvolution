import pygame as _pygame

import json as _json

class Spritesheet:  
    def __init__(self, filename) -> None:
        self.filename = filename
        self.sprite_sheet = _pygame.image.load(filename).convert()
        self.meta_data = self.filename.replace("png", "json")
        with open(self.meta_data) as file:
            self.image_data = _json.load(file)

    def _get_sprite(self, x, y, width, height, colourkey) -> _pygame.Surface:
        sprite = _pygame.Surface((width, height))
        sprite.set_colorkey(colourkey)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite
    
    def load_sprite(self, name, colourkey=(0, 0, 0)) -> _pygame.Surface:
        sprite = self.image_data["frames"][name]["frame"]
        
        return self._get_sprite(sprite["x"], sprite["y"], sprite["w"], sprite["h"], colourkey)