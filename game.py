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
from pygame.locals import *
import sys
import math


background = None
tents = []
enemies = []
optionbars = []
selectbars = []
keypressed = False
framecounter = 0
trees = []
stones = []
icons = []
workers = []
loot = []
envbuildings = []
towerthrown = []
grasses = []

class Spear(Actor):
    def __init__(self):
        super().__init__('rockammo')
        self.active = True
        self.direction = 'none'
        self.set = False

    def update(self):
        if not self.set:
            self.pos = dave.pos
            if dave.image == 'dave_wu*':
                print("dave up bro")
            self.set = True


class Icon(Actor):
    def __init__(self):
        if len(icons) < 1:
            super().__init__('plus')
        if len(icons) == 1:
            super().__init__('barricade_icon')
        if len(icons) == 2:
            super().__init__('tower_icon')
        if len(icons) == 3:
            super().__init__('plus')

        self.active = True
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
class Towerthrown(Actor):
    def __init__(self):
        super().__init__('rockammo')
        self.active = False
        self.set = False
    def update(self):
        pass

class Smalltower(Actor):
    def __init__(self):
        super().__init__('tower')
        self.type = 'tower'
        self.maxhp = 10
        self.hp = self.maxhp
        self.active = False
        self.building = True
        self.harmingentities = []
        self.targets = []
        self.radius = 250
        self.towerthrown = []
        self.canplace = False


        self.holding_mouse = False
    def update(self):
        global mouse_holded
        mousepos = pygame.mouse.get_pos(2)
        mousestate = pygame.mouse.get_pressed(3)
        if self.building:
            self.pos = mousepos
            if mousestate[0]:
                if not mouse_holded:
                    if self.canplace:
                        self.building = False
                    mouse_holded = True
        else:
            self.active = True
        if self.active:
            for foe in enemies:
                x1, y1 = self.pos
                x2, y2 = foe.pos
                distance = math.hypot(x1 - x2, y1 - y2)
                if distance < self.radius:
                    if foe not in self.targets:
                        self.targets.append(foe)
                    if len(self.targets) > 0:
                        if not foe.dead:
                            if framecounter %50 == 0:
                                self.towerthrown.append(Towerthrown())
                                self.towerthrown[-1].pos = self.pos
                            if self.towerthrown != []:
                                if self.towerthrown[-1].x < self.targets[0].x:
                                    self.towerthrown[-1].x += 5
                                if self.towerthrown[-1].x > self.targets[0].x:
                                    self.towerthrown[-1].x -= 5
                                if self.towerthrown[-1].y < self.targets[0].y:
                                    self.towerthrown[-1].y += 5
                                if self.towerthrown[-1].y > self.targets[0].y:
                                    self.towerthrown[-1].y -= 5
                                if self.targets[0].colliderect(self.towerthrown[-1]):
                                    self.targets[0].hp -= 1
                                    self.towerthrown.remove(self.towerthrown[-1])
                        if self.targets[0].dead:
                            self.targets.remove(self.targets[0])
                            for thrown in self.towerthrown:
                                self.towerthrown.remove(thrown)
                        break
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
            if framecounter % 500 == 0:
                towerthrown.append(Towerthrown())
                towerthrown[-1].pos = self.pos
            if self.hp <= 0:
                for harmingbug in self.harmingentities:
                    harmingbug.speed = 0.5
                envbuildings.remove(self)



class Grass(Actor):
    def __init__(self):
        super().__init__('grass2')
        self.maxwork = 20
        self.working_status = 0
        self.x = randint(200, WIDTH - 400)
        self.y = choice([100, HEIGHT - 100])
    def update(self):

        if self.colliderect(dave):
            if framecounter %10 == 0:
                self.working_status += dave.workpower
            if self.working_status >= self.maxwork:
                dave.grass += randint(1, 2)
                grasses.remove(self)
        for worker in workers:
            if self.colliderect(worker):
                if framecounter %10 == 0:
                    self.working_status += dave.workpower
                if self.working_status >= self.maxwork:
                    dave.grass += randint(1, 2)
                    grasses.remove(self)
class Stone(Actor):
    def __init__(self):
        super().__init__('stone')
        self.x = WIDTH - 250
        self.y = HEIGHT - 200
class Rock(Actor):
    def __init__(self):
        super().__init__('rock')
        self.active = False
        self.maxangle = randint(310, 400)

    def fall(self):
        if self.angle < self.maxangle:
            self.angle += 5
            self.y += 1

    def update(self):
        if not self.active:
            self.pos = stones[0].pos
            print('rock')
            self.active = True
        else:
            self.fall()
        if self.active:
            if self.colliderect(dave):
                dave.stone += 1
                loot.remove(self)
            for worker in workers:
                if self.colliderect(worker):
                    dave.stone += 1
                    loot.remove(self)
class Tree(Actor):
    def __init__(self):
        super().__init__('tree')
        self.x = 250
        self.y = 200

class Branch(Actor):
    def __init__(self):
        super().__init__(choice(['branch_1', 'branch_2']))
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
        for worker in workers:
            if self.colliderect(worker):
                dave.wood += 1
                loot.remove(self)

class Barricade(Actor):
    def __init__(self):
        super().__init__('barricade')
        self.maxhp = 20
        self.hp = self.maxhp
        self.active = False
        self.building = True
        self.harmingentities = []
        self.rotated = False
        self.holding_mouse = False
        self.type = 'barricade'
        self.canplace = False
    def update(self):
        global mouse_holded
        mousepos = pygame.mouse.get_pos(2)
        mousestate = pygame.mouse.get_pressed(3)
        if self.building:
            self.pos = mousepos
            if mousestate[0]:
                if not mouse_holded:
                    if self.canplace:
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
        self.hotbar = 0
        self.framecounter = 0
        self.frame = 1
        self.pressedkey = False
        self.speed = 2
        self.goingleft = False
        self.x = WIDTH / 2
        self.y = HEIGHT / 2 + 40
        self.wood = 0 + 50
        self.leather = 0 + 20
        self.stone = 0 + 30
        self.xp = 20
        self.lvl = 0
        self.buildingradius = 150
        self.spears = 0
        self.active_throwns = []
        self.canthrow = False
        self.throwed_time = pygame.time.get_ticks() / 60
        self.cooldown = 10
        self.grass = 0
        self.workpower = 1
    def update(self):
        #print(pygame.time.get_ticks() / 1000)
        #print(len(self.active_throwns))
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
        # for event in pygame.event.get():
        #     if event.type == pygame.MOUSEWHEEL:
        #         print(event.x,event.y)


        if not keyboard.w and not keyboard.s and not keyboard.a and not keyboard.d and not keyboard.space:
            self.idle_animate()
            self.pressedkey = False


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

        if keyboard.space:
            if self.canthrow:
                self.canthrow = False
                self.active_throwns.append(Spear())
            else:
                pass
        if not self.canthrow:
            if self.throwed_time + self.cooldown < pygame.time.get_ticks() / 60:
                self.throwed_time = pygame.time.get_ticks() / 60 + 2
                self.canthrow = True

        if dave.xp == 25:
            workers.append(Worker())
            workers[-1].pos = tents[-1].pos
            dave.xp += 1

        if dave.xp == 75:
            workers.append(Worker())
            workers[-1].pos = tents[-1].pos
            dave.xp += 1

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
        self.y = choice([-30, HEIGHT + 30, HEIGHT / 2])
        if self.y == HEIGHT / 2:
            self.x = choice([-30, WIDTH + 30])
        else:
            self.x = choice([-30, WIDTH + 30, WIDTH / 2])

        self.frame = 1
        self.hp = 1
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
        if self.colliderect(dave) or self.hp <= 0:
            self.die()
        for worker in workers:
            if self.colliderect(worker):
                self.die()
        if self.dead:
            if self.frame < 6:
                self.image = f'bug_die{self.frame}'
            if self.frame > 15:
                enemies.remove(self)

class Wolf(Bug):
    def __init__(self):
        super().__init__()
        self.image = 'wolf_wd_1'
        self.hp = 5
    def update(self):

        if framecounter %5 == 0:
            self.frame += 1
        if not self.dead:
            if self.frame > 5:
                self.frame = 1
            if self.frame < 6:
                self.image = f'wolf_wd_{self.frame}'
            if self.x < WIDTH / 2:
                self.x += self.speed
            elif self.x > WIDTH / 2:
                self.x -= self.speed
            if self.y < HEIGHT / 2:
                self.y += self.speed
            if self.y > HEIGHT / 2:
                self.y -= self.speed
        if self.hp <= 0:
            self.die()
        for worker in workers:
            if self.colliderect(worker):
                pass
        if self.dead:
            if self.frame < 6:
                self.image = f'bug_die{self.frame}'
            if self.frame > 15:
                dave.leather += 1
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
        dave.throwed_time = pygame.time.get_ticks() / 60
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
            global mouse_holded
            if mousestate[0]:
                if not mouse_holded:
                    if icons[0].left < mousepos[0] < icons[0].right:
                        if icons[0].top < mousepos[1] < icons[0].bottom:
                            if icons[0].active:
                                if dave.xp >= 50:
                                    if len(tents) < 2:
                                        for tent in tents:
                                            tent.x -= 30 * len(tents)
                                        tents.append(Tent())
                                        workers.append(Worker())
                                        tents[-1].x += 30 * len(tents)
                                        workers[-1].pos = tents[-1].pos
                                        mouse_holded = True
                                    if dave.xp >= 100:
                                        if len(tents) < 3:
                                            for tent in tents:
                                                tent.x -= 30 * len(tents)
                                            tents.append(Tent())
                                            workers.append(Worker())
                                            tents[-1].x += 30 * len(tents)
                                            workers[-1].pos = tents[-1].pos
                                            mouse_holded = True


                    if icons[1].left < mousepos[0] < icons[1].right:
                        if icons[1].top < mousepos[1] < icons[1].bottom:
                            if dave.wood >= 8:
                                if len(envbuildings) != 0:
                                    if not envbuildings[-1].building:
                                        envbuildings.append(Barricade())
                                        dave.wood -= 8
                                        mouse_holded = True
                                else:
                                    envbuildings.append(Barricade())
                                    dave.wood -= 8
                                    mouse_holded = True

                    elif icons[2].left < mousepos[0] < icons[2].right:
                        if icons[2].top < mousepos[1] < icons[2].bottom:
                            if dave.wood >= 10:
                                if dave.stone >= 10:
                                    if len(envbuildings) != 0:
                                        if not envbuildings[-1].building:
                                            envbuildings.append(Smalltower())
                                            dave.wood -= 10
                                            dave.stone -= 10
                                            mouse_holded = True
                                    else:
                                        envbuildings.append(Smalltower())
                                        dave.wood -= 10
                                        dave.stone -= 10
                                        mouse_holded = True
            else:
                mouse_holded = False

            if len(workers) > 0:
                if dave.xp > 50:
                    icons[0].active = True
            else:
                icons[0].active = False


            if dave.wood >= 8:
                icons[1].active = True
            else:
                icons[1].active = False

            towers_count = sum(1 for x in envbuildings if isinstance(x, Smalltower))

            if dave.wood >= 10 and dave.stone >= 10:
                if towers_count < len(workers) + 1:
                    icons[2].active = True
                else:
                    icons[2].active = False
            else:
                icons[2].active = False


            for worker in workers:
                worker.update()

            for item in loot:
                item.update()

        framecounter += 1
        if framecounter > 1000:
            framecounter = 0
        if pygame.time.get_ticks() / 1000 > 60:
            if framecounter % 999 == 0:
                enemies.append(Wolf())
        if framecounter %660 == 0:
            enemies.append(Bug())

            if len(loot) < 10:
                loot.append(Branch())
                loot.append(Rock())
        dave.update()

        for bug in enemies:
            bug.update()



        for building in envbuildings:
            if building.building:
                x1, y1 = building.pos
                x2, y2 = dave.pos
                distance = math.hypot(x1 - x2, y1 - y2)
                if distance < dave.buildingradius:
                    building.canplace = True
                else:
                    building.canplace = False
                    actor_x.pos = building.pos
            building.update()
        for thrown in towerthrown:
            thrown.update()
        for thrown in dave.active_throwns:
            thrown.update()
        for grass in grasses:
            grass.update()
        if len(grasses) < 2:
            if framecounter %880 == 0:
                grasses.append(Grass())

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
            for grass in grasses:
                grass.draw()
            for stone in stones:
                stone.draw()
            for tent in tents:
                tent.draw()
            if dave.goingleft == True:
                screen.blit(flip(dave._surf, True, False), dave.topleft)
            else:
                dave.draw()
            for worker in workers:
                worker.draw()
                for grass in grasses:
                    if grass.colliderect(worker):
                        screen.draw.filled_rect(
                            Rect((grass.x - grass.width / 3, grass.y + grass.height / 2), (grass.maxwork, 5)),(200, 200, 0))
                        screen.draw.filled_rect(
                            Rect((grass.x - grass.width / 3, grass.y + grass.height / 2), (grass.working_status, 5)),(0, 0, 200))
            for icon in icons:
                if icon.active:
                    icon.draw()
            for item in loot:
                item.draw()

            for build in envbuildings:
                build.draw()
                if build.building:
                    screen.draw.circle((dave.pos), dave.buildingradius, (0, 50 ,200))
                if build.type == 'tower':
                    for thrown in build.towerthrown:
                        thrown.draw()
                if not build.canplace:
                    actor_x.draw()
                if build.active:
                    if 0 < build.hp < build.maxhp:
                        if build.maxhp > 50:
                            screen.draw.filled_rect(Rect((build.x - build.width / 4, build.y - 30), (build.maxhp / 2, 5)), (200, 0, 0))
                            screen.draw.filled_rect(Rect((build.x - build.width / 4, build.y - 30), (build.hp / 2, 5)), (0, 200, 0))
                        else:
                            screen.draw.filled_rect(Rect((build.x - build.width / 4, build.y - 30), (build.maxhp, 5)), (200, 0, 0))
                            screen.draw.filled_rect(Rect((build.x - build.width / 4, build.y - 30), (build.hp, 5)), (0, 200, 0))
            for thrown in dave.active_throwns:
                thrown.draw()
            for grass in grasses:
                if grass.colliderect(dave):
                    screen.draw.filled_rect(Rect((grass.x - grass.width / 3, grass.y + grass.height / 2), (grass.maxwork, 5)), (200, 200, 0))
                    screen.draw.filled_rect(Rect((grass.x - grass.width / 3, grass.y + grass.height / 2), (grass.working_status, 5)), (0, 0, 200))
            for hotbar in hotbars:
                hotbar.draw()

            #screen.draw.filled_rect(Rect((WIDTH - 60, 10), (50, 200)), (200, 200, 0))
            screen.blit('branch',(WIDTH - 100, 10))
            screen.draw.text(f' x {dave.wood}', (WIDTH - 70 , 20), color='black')
            screen.blit('rock', (WIDTH - 94, 50))
            screen.draw.text(f' x {dave.stone}', (WIDTH - 70, 55), color='black')
            screen.blit('grassfiber',(WIDTH - 98, 80))
            screen.draw.text(f' x {dave.grass}', (WIDTH - 70, 88), color='black')
            screen.blit('leather',(WIDTH - 100, 110))
            screen.draw.text(f' x {dave.leather}', (WIDTH - 70, 118), color='black')


            screen.draw.text(f'XP: {dave.xp}', (WIDTH / 2, 10), color='black')


gmstate = Gamestate()
enemies.append(Bug())
tents.append(Tent())
dave = Dave()
actor_x = Actor('actor_x')
trees.append(Tree())
stones.append(Stone())
grasses.append(Grass())

hotbars = []
for i in range(0, 8):
    thislen = len(hotbars)
    hotbars.append(Actor('hotbar'))
    hotbars[-1].bottom = HEIGHT - 10
    if thislen < 2:
        hotbars[-1].left = WIDTH / 3
    else:
        hotbars[-1].left = hotbars[thislen - 1].right + 5
hotbars.append(Actor('active_hotbar'))
hotbars[-1].pos = hotbars[0].pos
icons.append(Icon())
icons.append(Icon())
icons[-1].left = icons[0].right + 10
icons.append(Icon())
icons[-1].left = icons[1].right + 10

def on_mouse_down(pos, button):
    print("Mouse button", button, "clicked at", pos)
    if gmstate.is_game:
        if button == mouse.WHEEL_UP:
                    print('up')
                    dave.hotbar += 1
                    if dave.hotbar > 7:
                        dave.hotbar = 7
                    hotbars[-1].pos = hotbars[dave.hotbar].pos
        elif button == mouse.WHEEL_DOWN:
                    dave.hotbar -= 1
                    if dave.hotbar < 0:
                        dave.hotbar = 0
                    hotbars[-1].pos = hotbars[dave.hotbar].pos


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
