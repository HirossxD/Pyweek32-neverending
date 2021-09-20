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
loot = []
envbuildings = []

class Worker(Actor):
    def __init__(self):
        super().__init__('dave_wd_1')
        self.dx = choice([-1, 1])
        self.dy = choice([-1, 1])
    def update(self):
        self.x += self.dx
        self.y += self.dy
        if framecounter %200 == 0:
            self.dx = randint(-1, 1)
            self.dy = randint(-1, 1)
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

class Branch(Actor):
    def __init__(self):
        super().__init__('branch')
        self.active = False
        self.maxangle = randint (310, 400)
    def fall(self):
        if self.angle < self.maxangle:
            self.angle += 5
            self.y += 1
    def update(self):
        if not self.active:
            self.pos = trees[0].pos
            print('branch')
            self.active = True
        else:
            self.fall()
        if self.colliderect(dave):
            dave.wood += 1
            loot.remove(self)

class Barricade(Actor):
    def __init__(self):
        super().__init__('barricade')
        self.hp = 20
        self.active = False
        self.building = True
        self.harmingentities = []
        self.rotated = False
        self.holding_mouse = False
    def update(self):
        global mouse_holded
        mousepos = pygame.mouse.get_pos(2)
        mousestate = pygame.mouse.get_pressed(3)
        if self.building:
            self.pos = mousepos
            if mousestate[0]:
                if not mouse_holded:
                    self.building = False
                    mouse_holded = True

            elif mousestate[2]:
                if self.rotated:
                    if not self.holding_mouse:
                        self.angle -= 90
                        self.rotated = False
                        self.holding_mouse = True
                else:
                    if not self.holding_mouse:
                        self.angle += 90
                        self.rotated = True
                        self.holding_mouse = True
            else:
                self.holding_mouse = False
        else:
            self.active = True

        if self.active:
            for bug in enemies:
                if self.colliderect(bug):
                    if self.active:
                        if bug not in self.harmingentities:
                            self.harmingentities.append(bug)
                        for harmingbug in self.harmingentities:
                            harmingbug.speed = 0
                        if framecounter % 500 == 0:
                            self.hp -= 1




        if self.hp <= 0:
            for harmingbug in self.harmingentities:
                harmingbug.speed = 0.5
            envbuildings.remove(self)

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
        self.wood = 0 + 40
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


        if not keyboard.w and not keyboard.s and not keyboard.a and not keyboard.d:
            self.idle_animate()


        if keyboard.s:
            if not self.pressedkey:
                self.frame = 1
                self.pressedkey = True
            else:
                if not keyboard.a and not keyboard.d:
                    self.move_down_animate()
                self.y += self.speed
        if keyboard.w:
            if not self.pressedkey:
                self.frame = 1
                self.pressedkey = True
            else:
                if not keyboard.a and not keyboard.d:
                    self.move_up_animate()
                self.y -= self.speed
        if keyboard.d:
            if not self.pressedkey:
                self.frame = 1
                self.pressedkey = True
            else:
                self.move_horizontally_animate()
                self.x += self.speed
                self.goingleft = False
        if keyboard.a:
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
        self.x = choice([-30, WIDTH + 30, WIDTH / 2])
        self.y = choice([-30, HEIGHT + 30, HEIGHT / 2])
        self.frame = 1
        self.dead = False
        self.speed = 0.5
    def die(self):
        if not self.dead:
            dave.xp += 1
            self.frame = 1
        self.dead = True
    def update(self):

        if framecounter %5 == 0:
            self.frame += 1
        if not self.dead:
            if self.frame > 4:
                self.frame = 1
            if self.frame < 5:
                self.image = f'bug{self.frame}'
            if self.x < WIDTH / 2:
                self.x += self.speed
            elif self.x > WIDTH / 2:
                self.x -= self.speed
            if self.y < HEIGHT / 2:
                self.y += self.speed
            if self.y > HEIGHT / 2:
                self.y -= self.speed
        if self.colliderect(dave):
            self.die()
        for worker in workers:
            if self.colliderect(worker):
                self.die()
        if self.dead:
            if self.frame < 6:
                self.image = f'bug_die{self.frame}'
            if self.frame > 15:
                enemies.remove(self)


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
        if self.is_game: ########################################## game update
            mousestate = pygame.mouse.get_pressed(3)
            mousepos = pygame.mouse.get_pos(2)
            getcursor = pygame.mouse.get_cursor()
            global mouse_holded
            if mousestate[0]:
                if not mouse_holded:
                    if icons[0].left < mousepos[0] < icons[0].right:
                        if icons[0].top < mousepos[1] < icons[0].bottom:
                            if len(tents) < 3:
                                for tent in tents:
                                    tent.x -= 30 * len(tents)
                                tents.append(Tent())
                                workers.append(Worker())
                                tents[-1].x += 30 * len(tents)
                                workers[-1].pos = tents[-1].pos
                                mouse_holded = True

                                pass
                    if icons[1].left < mousepos[0] < icons[1].right:
                        if icons[1].top < mousepos[1] < icons[1].bottom:
                            if dave.wood >= 8:
                                envbuildings.append(Barricade())
                                dave.wood -= 8
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
            if len(loot) > 0:
                for item in loot:
                    item.update()

            framecounter += 1
            if framecounter > 1000:
                framecounter = 0
            if framecounter %480 == 0:
                loot.append(Branch())
                enemies.append(Bug())
            dave.update()
            for bug in enemies:
                bug.update()
            for building in envbuildings:
                building.update()




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
            for tree in trees:
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
            for item in loot:
                item.draw()
            for building in envbuildings:
                building.draw()
            screen.draw.text(f'Wood: {dave.wood}', (WIDTH / 2 - 110 + 50, 20), color='black')
gmstate = Gamestate()
enemies.append(Bug())
tents.append(Tent())
dave = Dave()
trees.append(Tree())
icons.append(Actor('plus'))
icons.append(Actor('barricade_icon'))
icons[-1].x += icons[0].width
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
