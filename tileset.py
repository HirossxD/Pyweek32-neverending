#!/usr/bin/env python3
import pgzrun
import pytmx
import pygame


# logger = logging.getLogger('towerdef')

WIDTH = 1152
HEIGHT = 1024
TITLE = "tower defence"


class Map:
    def __init__(self, filename):
        tile_map = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tile_map.width * tile_map.tilewidth
        self.height = tile_map.height * tile_map.tileheight
        print(tile_map)
        self.tmxdata = tile_map

    def render(self, surface):
        print(2)
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    print(x, y, gid)
                    tile = self.tmxdata.get_tile_image_by_gid(gid)
                    print(tile)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        print("3")
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.map = Map('maps/map.tmx')
        print("4")
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    #def load_data(self):
        #game_folder = os.path.dirname(__file__)
       # map_folder = os.path.join(game_folder, 'maps')

    def draw(self):
        print("1")
        self.screen.blit(self.map_img, self.map_rect)


g = Game()
g.draw()
pgzrun.go()