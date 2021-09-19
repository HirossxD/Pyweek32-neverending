import pgzero
import pygame
import pytmx
import pgzrun
from config import TITLE, WIDTH, HEIGHT
from statemachine import StateMachine, State
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pathlib import Path
from random import randint, choice
from pygame.transform import flip
import pygame
import sys
pg = sys.modules['__main__']
background = None
tents = []
enemies = []
optionbars = []
selectbars = []
keypressed = False
framecounter = 0
trees = []
icons = []
workers = []
class Worker(Actor):
    def __init__(self):
        super().__init__('dave_wd_1')
        self.dx = choice([-1, 1])
        self.dy = choice([-1, 1])
    def update(self):
        self.x += self.dx
        self.y += self.dy
        if framecounter %200 == 0:
            self.dx = randint(-1,1)
            self.dy = randint(-1,1)
        if self.right >= WIDTH:
                self.right = WIDTH
        if self.left <= 0:
                self.left = 0
        if self.top <= 0:
                self.top = 0
        if self.bottom >= HEIGHT:
                self.bottom = HEIGHT
class Tree(Actor):
    def __init__(self):
        super().__init__('tree')
        self.x = 250
        self.y = 200

class Dave(Actor):
    def __init__(self):
        super().__init__('dave_wd_1')
        self.framecounter = 0
        self.frame = 1
        self.pressedkey = False
        self.speed = 2
        self.goingleft = False
        self.x = WIDTH / 2
        self.y = HEIGHT / 2 + 40
        self.wood = 0
        self.leather = 0
        self.xp = 0
        self.lvl = 0



    def update(self):

        if self.framecounter >= 100:
            self.framecounter = 0
        if self.right >= WIDTH:
                self.right = WIDTH
        if self.left <= 0:
                self.left = 0
        if self.top <= 0:
                self.top = 0
        if self.bottom >= HEIGHT:
                self.bottom = HEIGHT
                    #self.bottom = HEIGHT


        if not keyboard.up and not keyboard.down and not keyboard.left and not keyboard.right:
            self.idle_animate()


        if keyboard.down:
            if not self.pressedkey:
                self.frame = 1
                self.pressedkey = True
            else:
                if not keyboard.left and not keyboard.right:
                    self.move_down_animate()
                self.y += self.speed
        if keyboard.up:
            if not self.pressedkey:
                self.frame = 1
                self.pressedkey = True
            else:
                if not keyboard.left and not keyboard.right:
                    self.move_up_animate()
                self.y -= self.speed
        if keyboard.right:
            if not self.pressedkey:
                self.frame = 1
                self.pressedkey = True
            else:
                self.move_horizontally_animate()
                self.x += self.speed
                self.goingleft = False
        if keyboard.left:
            if not self.pressedkey:
                self.frame = 1

                self.pressedkey = True
            else:
                self.move_horizontally_animate()
                self.x -= self.speed
                self.goingleft = True

    def idle_animate(self):
        global framecounter
        if framecounter % 10 == 0:
            self.frame += 1
        if self.frame > 3:
            self.frame = 1
        self.image = f'dave_idle_{self.frame}'


    def move_down_animate(self):
        self.framecounter += 1
        if self.framecounter % 5 == 0:
            self.frame += 1
        if self.frame > 5:
            self.frame = 1
        self.image = f'dave_wd_{self.frame}'

    def move_up_animate(self):
        self.framecounter += 1
        if self.framecounter % 5 == 0:
            self.frame += 1
        if self.frame > 5:
            self.frame = 1
        self.image = f'dave_wu_{self.frame}'
        if self.framecounter >= 100:
            self.framecounter = 0

    def move_horizontally_animate(self):
        self.framecounter += 1
        if self.framecounter % 5 == 0:
            self.frame += 1
        if self.frame > 6:
            self.frame = 1
        self.image = f'dave_ws_{self.frame}'
class Tent(Actor):
    def __init__(self):
        super().__init__('tent')
        self.x = WIDTH / 2
        self.y = HEIGHT / 2

class Bug(Actor):
    def __init__(self):
        super().__init__('bug1')
        self.x = randint(10, WIDTH - 10)
        self.y = randint(10, HEIGHT - 10)
        self.frame = 1
    def update(self):
        if framecounter %5 == 0:
            self.frame += 1
        if self.frame > 4:
            self.frame = 1
        if self.frame < 5:
            self.image = f'bug{self.frame}'
        if self.x < WIDTH / 2:
            self.x += 0.5
        elif self.x > WIDTH / 2:
            self.x -= 0.5
        if self.y < HEIGHT / 2:
            self.y += 0.5
        if self.y > HEIGHT / 2:
            self.y -= 0.5
        if keyboard.space:
            self.x = randint(10, WIDTH - 10)
            self.y = randint(10, HEIGHT - 10)
        if self.colliderect(dave) or self.colliderect(Worker()):
            self.x = -500
class Gamestate(StateMachine):
    mouse_holded = False
    init = State('init', initial= True)
    menu = State('Menu')
    game = State('Game')

    start = init.to(menu)
    play = menu.to(game)
    def on_play(self):
        print('starting game')
        pygame.mouse.set_cursor(pygame.cursors.broken_x)
    def on_start(self):
        print('initmenu')

        for i in range(0, 2):
            selectbars.append(Rect((WIDTH / 2 - 110 + (200 * i), HEIGHT / 3), (20, 50)))
        for i in range(0, 4):
            optionbars.append(Rect((WIDTH / 2 - 100, HEIGHT / 3 + (70 * i)), (200, 50)))

    def update(self):
        global keypressed
        global framecounter
        if self.is_init:
            self.start()
        if self.is_menu:
            if keyboard.down:
                if not keypressed:
                    for selectbar in selectbars:
                        if not selectbar.colliderect(optionbars[-1]):
                            if not selectbar.y > optionbars[-1].y:
                                selectbar.y += 70
                    keypressed = True
            elif keyboard.up:
                if not keypressed:
                    for selectbar in selectbars:
                        if not selectbar.colliderect(optionbars[0]):
                            if not selectbar.y < optionbars[0].y:
                                selectbar.y -= 70
                    keypressed = True
            else:
                keypressed = False
            if keyboard.space:
                if selectbars[0].y == optionbars[0].y:
                    self.play()
                if selectbars[0].y == optionbars[1].y:
                    print('help')
                if selectbars[0].y == optionbars[2].y:
                    print('options')
                elif selectbars[0].y == optionbars[-1].y:
                    exit()
        if self.is_game:
            mousestate = pygame.mouse.get_pressed(3)
            mousepos = pygame.mouse.get_pos(2)
            getcursor = pygame.mouse.get_cursor()
            global mouse_holded
            if mousestate[0]:
                if not mouse_holded:
                    if 0 < mousepos[0] < 27:
                        if 0 < mousepos[1] < 27:
                            if len(tents) < 3:
                                for tent in tents:
                                    tent.x -= 30 * len(tents)
                                tents.append(Tent())
                                workers.append(Worker())
                                tents[-1].x += 30 * len(tents)
                                workers[-1].pos = tents[-1].pos
                            else:
                                pass

                        mouse_holded = True
            else:
                mouse_holded = False
                if 0 < mousepos[0] < 27:
                    if 0 < mousepos[1] < 27:
                        if len(tents) + 1 > 3:
                            icons[0].image = 'cant_icon'
                    else:
                        icons[0].image = 'plus'

            if len(workers) > 0:
                for worker in workers:
                    worker.update()


            framecounter += 1
            if framecounter > 1000:
                framecounter = 0
            dave.update()
            for bug in enemies:
                bug.update()



    def draw(self):
        if self.is_menu:
            screen.clear()
            #screen.fill('white')
            for optionbar in optionbars:
                screen.draw.filled_rect(optionbar, (100, 200, 100))
            for selectbar in selectbars:
                screen.draw.filled_rect(selectbar, (150, 250, 50))
            screen.draw.text('PLAY GAME', (WIDTH / 2 - 110 + 50, HEIGHT / 3 + 15), fontsize = 30)
            screen.draw.text('HELP', (WIDTH / 2 - 110 + 80, HEIGHT / 3 + 85), fontsize=30)
            screen.draw.text('OPTIONS', (WIDTH / 2 - 110 + 60, HEIGHT / 3 + 155), fontsize=30)
            screen.draw.text('EXIT', (WIDTH / 2 - 110 + 80, HEIGHT / 3 + 225), fontsize=30)
        if self.is_game:
            screen.clear()
            background.draw()
            for bug in enemies:
                bug.draw()
            tree.draw()
            for tent in tents:
                tent.draw()
            if dave.goingleft == True:
                screen.blit(flip(dave._surf, True, False), dave.topleft)
            else:
                dave.draw()
            for worker in workers:
                worker.draw()
            for icon in icons:
                icon.draw()

gmstate = Gamestate()
enemies.append(Bug())
tents.append(Tent())
dave = Dave()
tree = Tree()
icons.append(Actor('plus'))
def update():
    gmstate.update()

def draw():
    gmstate.draw()


def init_game():
    global background
    level = pytmx.TiledMap('maps/map1.tmx')
    #layer = level.get_layer_by_name('actors')
    bglayer = level.get_layer_by_name('background')
    image = Path(bglayer.image[0])
    background = Actor(image.stem)


init_game()
pgzrun.go()
