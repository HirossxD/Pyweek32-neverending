import pgzero
import pygame
import pytmx
import pgzrun
from statemachine import StateMachine, State
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pathlib import Path
from random import randint, choice
from pygame.transform import flip
from pygame.locals import *
import math

# import tileset.py

TITLE = 'WILD CAMPERS'

WIDTH = 1252
HEIGHT = 768
offset = 100

background = None
tents = []
enemies = []
optionbars = []
buttonback = Rect((WIDTH / 2 - 160, HEIGHT - 100), (200, 50))
selectbars = []
keypressed = False
framecounter = 0
icons = []
workers = []
loot = []
envbuildings = []
grasses = []
hotbaritems = []


class ActiveHotbar(Actor):
    def __init__(self):
        super().__init__('active_hotbar')


class Hotbar(Actor):
    def __init__(self):
        super().__init__('hotbar')
        self.occupied = False

    def update(self):
        if Spear().icon.pos == self.pos:
            self.occupied = True


class Spear(Actor):
    def __init__(self):
        super().__init__('spear')
        self.throwed_direction = None
        self.pos = (-100, -200)
        self.active = True
        self.direction = 'none'
        self.set = False
        self.maxdurability = 20
        self.durability = self.maxdurability
        self.throwed = False
        self.icon = Actor('spear_hotbaricon')
        self.hotbarposition = 0
        self.harmful = False
        self.in_hand = False
        self.icon.angle = -45
        self.placedinhotbar = False

    def Throw(self):

        for hotbar in hotbars:
            if hotbar.pos == self.icon.pos:
                hotbar.occupied = False
                self.icon.pos = (-200, -200)
                break

        self.harmful = True
        self.throwed = True
        self.in_hand = False
        self.placedinhotbar = False
        if self.throwed_direction == None:
            self.durability -= 3
            self.throwed_direction = pygame.mouse.get_pos()

    def cleanup(self):
        if not self.harmful:
            dave.in_hand = None
            hotbaritems.remove(self)

    def update(self):
        # need optimisation later :D

        for hotbar in hotbars:
            if isinstance(hotbar, Hotbar):
                if not hotbar.occupied:
                    if not self.throwed:
                        if not self.harmful:
                            if not self.placedinhotbar:
                                self.icon.pos = hotbar.pos
                                hotbar.occupied = True
                                self.placedinhotbar = True
                    break
        for hotbar in hotbars:
            if isinstance(hotbar, ActiveHotbar):
                for item in hotbaritems:
                    if item.icon.pos == hotbar.pos:
                        item.in_hand = True
                    else:
                        item.in_hand = False

        if self.pos == self.throwed_direction:
            self.harmful = False

        if self.in_hand:
            if dave.idle:
                self.pos = (dave.x + 14, dave.y + 10 + dave.frame - 4)
                self.angle = 180
            if keyboard.s:
                self.pos = (dave.x + 15, dave.y + 10 + dave.frame)
                self.angle = 180
            if keyboard.w:
                self.pos = (dave.x + 15, dave.y + 10 + dave.frame * 2)
                self.angle = 0
            if keyboard.a:
                self.pos = (dave.x - dave.frame, dave.y + 10)
                self.angle = 90
            if keyboard.d:
                self.pos = (dave.x + dave.frame, dave.y + 10)
                self.angle = -90
        if not self.in_hand:
            if not self.throwed:
                self.pos = (-100, -200)
            elif self.throwed:
                if not self.set:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    rel_x, rel_y = mouse_x - self.x, mouse_y - self.y
                    self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90
                    self.set = True
                if self.right >= WIDTH - offset:
                    self.throwed_direction = self.pos
                for enemy in enemies:
                    if self.colliderect(enemy):
                        if not enemy.dead:
                            if self.harmful:
                                enemy.hp -= 2
                                self.throwed_direction = self.pos

                animate(self, duration=0.4, pos=self.throwed_direction)
                if abs(self.x - self.throwed_direction[0]) < self.height and abs(
                        self.y - self.throwed_direction[1]) < self.height:
                    self.throwed_direction = self.pos

        if self.durability <= 0:
            self.cleanup()


class Shield(Spear):
    def __init__(self):
        super().__init__()
        self.image = 'shield_back'
        self.icon = Actor('shield_hotbaricon')
        # polish to image shield back when going left

    def Block(self):
        for bug in enemies:
            if self.colliderect(bug):
                if not bug.knocked:
                    bug.hp -= 1
                    bug.knocked = True
                self.durability -= 1

    def cleanup(self):
        dave.in_hand = None
        dave.protected = False
        for hotbar in hotbars:
            if hotbar.pos == self.icon.pos:
                hotbar.occupied = False
                self.icon.pos = (-200, -200)

        hotbaritems.remove(self)

        # animate(bug, duration=0.4, pos=(knockpos_x, knockpos_y))

        # knockpos_x, knockpos_y = pygame.mouse.get_pos()
        #  a, b = pygame.Vector2(x,y)
        #  b = pygame.Vector2(x)
        #  c = a.distance_to(b)
        #
        # if a.distance_to(b) > 200:
        #     animate(bug, duration=0.4, pos=(knockpos_x, knockpos_y) )
        #     bug.speed = 0.5

        # if abs(dave.x - knockpos_x) > 30 and abs(knockpos_y - dave.y) > 30:
        #     bug.pos = (knockpos_x, knockpos_y)
        #     self.throwed_direction = self.pos

    def Throw(self):
        self.Block()


class Icon(Actor):
    def __init__(self):
        if len(icons) < 1:
            super().__init__('plus')
        elif len(icons) == 1:
            super().__init__('barricade_icon')
        elif len(icons) == 2:
            super().__init__('tower_icon')
        elif len(icons) == 3:
            super().__init__('spear_icon')
        elif len(icons) == 4:
            super().__init__('shield_icon')
        elif len(icons) == 5:
            super().__init__('tentrepair_icon')
        else:
            super().__init__('plus')

        self.active = False


class Worker(Actor):
    def __init__(self):
        super().__init__('wildman_wd_1')
        self.dx = choice([-1, 1])
        self.dy = choice([-1, 1])
        self.rand = randint(50, 500)
        self.frame = 1

    def update(self):
        if framecounter % 8 == 0:
            self.frame += 1
            if self.frame > 3:
                self.frame = 1
            if self.dy > 0:
                self.image = f'worker_wd_{self.frame}'
            if self.dy < 0:
                self.image = f'worker_wu_{self.frame}'
            if self.dy == 0 and self.dx == 0:
                self.image = f'worker_idle_{self.frame}'
            if self.dy == 0:
                if self.dx > 0:
                    self.image = f'worker_wr_{self.frame}'
                if self.dx < 0:
                    self.image = f'worker_wl_{self.frame}'

        self.x += self.dx
        self.y += self.dy
        if framecounter % self.rand == 0:
            self.dx = randint(-1, 1)
            self.dy = randint(-1, 1)
            self.rand = randint(50, 500)

        if self.right >= WIDTH - offset:
            self.dx *= -1
            self.right = WIDTH - offset - 1

        if self.left <= 0:
            self.left = 1
            self.dx *= -1
        if self.top <= 0:
            self.top = 1
            self.dy *= -1
        if self.bottom >= HEIGHT:
            self.bottom = HEIGHT - 1
            self.dy *= -1

        if self.colliderect(Stone()):
            if int(self.right) in range(int(Stone().left) - 5, int(Stone().left) + 5):
                if not self.y > Stone().bottom:
                    self.right = Stone().left
            if int(self.left) in range(int(Stone().right) - 5, int(Stone().right) + 5):
                if not self.y > Stone().bottom:
                    self.left = Stone().right
            if int(self.bottom) in range(int(Stone().y) - 5, int(Stone().y) + 5):
                self.bottom = Stone().y - 5
            if int(self.top) in range(int(Stone().y) - 5, int(Stone().y) + 5):
                self.top = Stone().y + 5

        if self.colliderect(Grass()):
            self.dx = 0
            self.dx = 0
            if Grass().working_status >= 20:
                self.dx = choice([-1, 1])
                self.dy = choice([-1, 1])


class Towerthrown(Actor):
    def __init__(self):
        super().__init__(choice(['rockammo', 'rock_1', 'rock_2']))
        self.active = False
        self.set = False

    def update(self):
        pass


class Smalltower(Actor):
    def __init__(self):
        super().__init__('tower')
        self.type = 'tower'
        self.maxhp = 20
        self.hp = self.maxhp + 1
        self.active = False
        self.building = True
        self.harmingentities = []
        self.targets = []
        self.radius = 250
        self.towerthrown = []
        self.canplace = False

        self.holding_mouse = False

    def update(self):

        mousepos = pygame.mouse.get_pos(2)
        mousestate = pygame.mouse.get_pressed(3)
        if self.building:
            self.pos = mousepos
            if mousestate[0]:
                if not gmstate.mouse_holded:
                    if self.canplace:
                        self.building = False
                    mouse_holded = True
        else:
            self.active = True
        if self.active:
            if self.hp == self.maxhp + 1:
                sounds.build.play()
                self.hp = self.maxhp
            for foe in enemies:
                x1, y1 = self.pos
                x2, y2 = foe.pos
                distance = math.hypot(x1 - x2, y1 - y2)
                if distance < self.radius:
                    if foe not in self.targets:
                        self.targets.append(foe)
                    if len(self.targets) > 0:
                        if not foe.dead:
                            if framecounter % 50 == 0:
                                self.towerthrown.append(Towerthrown())
                                self.towerthrown[-1].pos = self.pos
                            if self.towerthrown != []:
                                animate(self.towerthrown[-1], tween='linear', duration=0.30, pos=self.targets[0].pos)
                                if abs(self.towerthrown[-1].x - self.targets[0].x) < 3 and abs(
                                        self.towerthrown[-1].y - self.targets[0].y) < 3:
                                    self.towerthrown[-1].pos = self.targets[0].pos

                                if self.targets[0].colliderect(self.towerthrown[-1]):
                                    self.targets[0].hp -= 1
                                    self.towerthrown.remove(self.towerthrown[-1])
                        if self.targets[0].dead:
                            self.targets.remove(self.targets[0])
                            for thrown in self.towerthrown:
                                self.towerthrown.remove(thrown)
                        break

            if self.hp <= 0:
                for harmingbug in self.harmingentities:
                    harmingbug.speed = 0.5
                for branch in range(1, randint(2, 8)):
                    loot.append(Branch())
                    loot[-1].pos = self.pos
                envbuildings.remove(self)

        if self.building:
            if len(envbuildings) > 1:
                if self.colliderect(envbuildings[0]):
                    self.canplace = False
            if len(envbuildings) > 2:
                if self.colliderect(envbuildings[1]):
                    self.canplace = False
            if len(envbuildings) > 3:
                if self.colliderect(envbuildings[2]):
                    self.canplace = False
            if len(envbuildings) > 4:
                if self.colliderect(envbuildings[3]):
                    self.canplace = False
            if len(envbuildings) > 5:
                if self.colliderect(envbuildings[4]):
                    self.canplace = False
            if len(envbuildings) > 6:
                if self.colliderect(envbuildings[5]):
                    self.canplace = False
            if len(envbuildings) > 7:
                if self.colliderect(envbuildings[6]):
                    self.canplace = False
            if len(envbuildings) > 8:
                if self.colliderect(envbuildings[7]):
                    self.canplace = False


class Grass(Actor):
    def __init__(self):
        super().__init__('grass2')
        self.maxwork = 20
        self.working_status = 0
        self.x = randint(200, WIDTH - 400)
        self.y = choice([100, HEIGHT - 100])

    def update(self):

        if self.colliderect(dave):
            if framecounter % 10 == 0:
                self.working_status += dave.workpower
            if self.working_status >= self.maxwork:
                dave.grass += randint(1, 2)
                grasses.remove(self)
        for worker in workers:
            if self.colliderect(worker):
                worker.dx = 0
                worker.dy = 0
                if framecounter % 10 == 0:
                    self.working_status += dave.workpower
                if self.working_status >= self.maxwork:
                    worker.dx = choice([-1, 1])
                    worker.dy = choice([-1, 1])
                    dave.grass += randint(1, 2)
                    if not dave.colliderect(self):
                        grasses.remove(self)
                    break


class Stone(Actor):
    def __init__(self):
        super().__init__('stone')
        self.x = WIDTH - 250 - offset
        self.y = HEIGHT - 200


class Rock(Actor):
    def __init__(self):
        super().__init__(choice(['rockammo', 'rock_1', 'rock_2']))
        self.active = False
        self.maxangle = randint(310, 400)

    def fall(self):
        if self.angle < self.maxangle:
            self.angle += 5
            self.y += 1

    def update(self):
        if not self.active:
            self.pos = stone.pos
            print('rock')
            self.active = True
        else:
            self.fall()
        if self.active:
            if self.colliderect(dave):
                dave.stone += 1
                loot.remove(self)
            elif workers != []:
                for worker in workers:
                    if self.colliderect(worker):
                        dave.stone += 1
                        loot.remove(self)
                        break


class Tree(Actor):
    def __init__(self):
        super().__init__('tree')
        self.x = 250 - offset
        self.y = 200


class Branch(Actor):
    def __init__(self):
        super().__init__(choice(['branch_1', 'branch_2']))
        self.active = False
        self.maxangle = randint(310, 400)
        self.pos = tree.pos

    def fall(self):
        if self.angle < self.maxangle:
            self.angle += 5
            self.y += 1

    def update(self):

        self.fall()
        if self.colliderect(dave):
            dave.wood += 1
            loot.remove(self)
        elif workers != []:
            for worker in workers:
                if self.colliderect(worker):
                    dave.wood += 1
                    loot.remove(self)
                    break


class Barricade(Actor):
    def __init__(self):
        super().__init__('barricade_rotated')
        self.maxhp = 20
        self.hp = self.maxhp + 1
        self.active = False
        self.building = True
        self.harmingentities = []
        self.rotated = False
        self.holding_mouse = False
        self.type = 'barricade'
        self.canplace = False

    def update(self):
        mousepos = pygame.mouse.get_pos(2)
        mousestate = pygame.mouse.get_pressed(3)
        if self.building:
            self.pos = mousepos
            if mousestate[0]:
                if not gmstate.mouse_holded:
                    if self.canplace:
                        self.building = False
                    mouse_holded = True

            elif mousestate[2]:
                if self.rotated:
                    if not self.holding_mouse:
                        # self.image = 'barricade'
                        self.rotated = False
                        self.angle -= 90
                        self.holding_mouse = True
                else:
                    if not self.holding_mouse:
                        # self.image = 'barricade_rotated'
                        self.rotated = True
                        self.angle += 90
                        self.holding_mouse = True
            else:
                self.holding_mouse = False
        else:
            self.active = True

        if self.active:
            if self.hp == self.maxhp + 1:
                sounds.build.play()
                self.hp = self.maxhp
            for bug in enemies:
                if self.colliderect(bug):
                    if self.active:
                        if bug not in self.harmingentities:
                            self.harmingentities.append(bug)
                        for harmingbug in self.harmingentities:
                            harmingbug.speed = 0
                        if framecounter % 500 == 0:
                            self.hp -= 1
        if self.building:
            if len(envbuildings) > 1:
                if self.colliderect(envbuildings[0]):
                    self.canplace = False
            if len(envbuildings) > 2:
                if self.colliderect(envbuildings[1]):
                    self.canplace = False
            if len(envbuildings) > 3:
                if self.colliderect(envbuildings[2]):
                    self.canplace = False
            if len(envbuildings) > 4:
                if self.colliderect(envbuildings[3]):
                    self.canplace = False
            if len(envbuildings) > 5:
                if self.colliderect(envbuildings[4]):
                    self.canplace = False
            if len(envbuildings) > 6:
                if self.colliderect(envbuildings[5]):
                    self.canplace = False
            if len(envbuildings) > 7:
                if self.colliderect(envbuildings[6]):
                    self.canplace = False
            if len(envbuildings) > 8:
                if self.colliderect(envbuildings[7]):
                    self.canplace = False

        if self.hp <= 0:
            for harmingbug in self.harmingentities:
                harmingbug.speed = 0.5
            for branch in range(1, randint(2, 4)):
                loot.append(Branch())
                loot[-1].pos = self.pos
            envbuildings.remove(self)


class Dave(Actor):
    def __init__(self):
        super().__init__('wildman_wd_1')
        self.hotbar = 0
        self.framecounter = 0
        self.frame = 1
        self.pressedkey = False
        self.speed = 2
        self.goingleft = False
        self.x = (WIDTH - offset) / 2
        self.y = HEIGHT / 2 + 40
        self.wood = 0  # + 50
        self.leather = 0  # + 20
        self.stone = 0  # + 50
        self.grass = 0  # + 50
        self.xp = 0  # + 50
        self.lvl = 0
        self.maxhp = 30
        self.hp = self.maxhp
        self.buildingradius = 150
        self.spears = 0
        self.active_throwns = []
        self.canthrow = False
        self.throwed_time = pygame.time.get_ticks() / 60
        self.cooldown = 10
        self.encumbered = False
        self.hotbarusage = 0
        self.workpower = 1
        self.idle = False
        self.wolftimer = 30
        self.wolfgrouptimer = 0
        self.dead = False
        self.protected = False
        self.in_hand = None

    def update(self):
        if keyboard.K_1:
            hotbars[-1].pos = hotbars[0].pos
        if keyboard.K_2:
            hotbars[-1].pos = hotbars[1].pos
        if keyboard.K_3:
            hotbars[-1].pos = hotbars[2].pos
        if keyboard.K_4:
            hotbars[-1].pos = hotbars[3].pos
        if keyboard.K_5:
            hotbars[-1].pos = hotbars[4].pos
        if keyboard.K_6:
            hotbars[-1].pos = hotbars[5].pos
        if keyboard.K_7:
            hotbars[-1].pos = hotbars[6].pos
        if keyboard.K_8:
            hotbars[-1].pos = hotbars[7].pos
        ##godmode
        # if keyboard.p:
        #     if tents:
        #         tents[-1].hp -= 1
        # if keyboard.g:
        #     self.wood = 50
        #     self.leather = 50
        #     self.stone = 50
        #     self.grass = 50
        #     self.hp = self.maxhp
        #     self.xp = 100
        #     if len(enemies) < 3:
        #         enemies.append(Wolf())
        #         workers.append(Worker())
        #     for tent in tents:
        #         tent.hp = tent.maxhp

        if self.framecounter >= 100:
            self.framecounter = 0
        if self.right >= WIDTH - offset:
            self.right = WIDTH - offset
        if self.left <= 0:
            self.left = 0
        if self.top <= 0:
            self.top = 0
        if self.bottom >= HEIGHT:
            self.bottom = HEIGHT

        if self.hp < self.maxhp:
            if framecounter % 1000 == 0:
                self.hp += 1

        if self.colliderect(Stone()):
            if int(self.right) in range(int(Stone().left) - 5, int(Stone().left) + 5):
                if not self.y > Stone().bottom:
                    self.right = Stone().left
            if int(self.left) in range(int(Stone().right) - 5, int(Stone().right) + 5):
                if not self.y > Stone().bottom:
                    self.left = Stone().right
            if int(self.bottom) in range(int(Stone().y) - 5, int(Stone().y) + 5):
                self.bottom = Stone().y - 5
            if int(self.top) in range(int(Stone().y) - 5, int(Stone().y) + 5):
                self.top = Stone().y + 5
        for tent in tents:
            if self.colliderect(tent):
                if int(self.right) in range(int(tent.left) - 5, int(tent.left) + 5):
                    if not self.y > tent.bottom:
                        self.right = tent.left
                if int(self.left) in range(int(tent.right) - 5, int(tent.right) + 5):
                    if not self.y > tent.bottom:
                        self.left = tent.right
                if int(self.bottom) in range(int(tent.y) - 5, int(tent.y) + 5):
                    self.bottom = tent.y - 5
                if int(self.top) in range(int(tent.y) - 5, int(tent.y) + 5):
                    self.top = tent.y + 5
                    # self.bottom = HEIGHT

        # for event in pygame.event.get():
        #     if event.type == pygame.MOUSEWHEEL:
        #         print(event.x,event.y)

        # if keyboard.l:
        #     workers.append(Worker())
        if not keyboard.w and not keyboard.s and not keyboard.a and not keyboard.d and not keyboard.space:
            self.goingleft = False
            self.idle_animate()
            self.pressedkey = False
            self.idle = True
        else:
            self.idle = False

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
                self.goingleft = False
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
            if len(tents) > 1:
                workers.append(Worker())
                workers[-1].pos = tents[-1].pos
                dave.xp += 1
        if not self.dead:
            if self.hp <= 0:
                self.dead = True

        if self.dead:
            if tents:
                self.pos = tents[0].pos
                if framecounter %50 == 0:
                    self.hp += 1
                    if self.hp >= self.maxhp:
                        self.dead = False

        for item in hotbaritems:
            if self.colliderect(item):
                if isinstance(item, Spear):
                    if item.throwed:
                        if not item.harmful:
                            for hotbar in hotbars:
                                if isinstance(hotbar, Hotbar):
                                    if not hotbar.occupied:
                                        item.throwed = False
                                        item.icon.pos = hotbar.pos
                                        item.set = False
                                        item.throwed_direction = None
                                        item.harmful = False
                                        break

                if isinstance(item, Shield):
                    if item.in_hand:
                        self.protected = True
                        break
        self.hotbarusage = 0
        for hotbar in hotbars:
            if isinstance(hotbar, Hotbar):
                if hotbar.occupied:
                    self.hotbarusage += 1
                    if self.hotbarusage >= 8:
                        dave.encumbered = True
                    else:
                        dave.encumbered = False

    def idle_animate(self):
        global framecounter
        if framecounter % 10 == 0:
            self.frame += 1
        if self.frame > 8:
            self.frame = 1
        self.image = f'wildman_idle_{self.frame}'

    def move_down_animate(self):
        self.framecounter += 1
        if self.framecounter % 5 == 0:
            self.frame += 1
        if self.frame > 4:
            self.frame = 1
        self.image = f'wildman_wd_{self.frame}'

    def move_up_animate(self):
        self.framecounter += 1
        if self.framecounter % 5 == 0:
            self.frame += 1
        if self.frame > 4:
            self.frame = 1
        self.image = f'wildman_wu_{self.frame}'
        if self.framecounter >= 100:
            self.framecounter = 0

    def move_horizontally_animate(self):
        self.framecounter += 1
        if self.framecounter % 5 == 0:
            self.frame += 1
        if self.frame > 8:
            self.frame = 1
        self.image = f'wildman_ws_{self.frame}'


class Tent(Actor):
    def __init__(self):
        super().__init__('tent')
        self.x = (WIDTH - offset) / 2
        self.y = HEIGHT / 2
        self.maxhp = 40
        self.hp = self.maxhp

    def update(self):
        for tent in tents:
            if self.colliderect(tent):
                self.speed = 0


            else:
                self.speed = 0.5

        for foe in enemies:
            if self.colliderect(foe):
                if not foe.dead:
                    foe.speed = 0
                    if framecounter % 50 == 0:
                        self.hp -= foe.damage / 2
            else:
                foe.speed = 0.5


class Bug(Actor):
    def __init__(self):
        super().__init__('bug1')
        self.y = choice([-30, HEIGHT + 30, HEIGHT / 2])
        if self.y == HEIGHT / 2:
            self.x = choice([-30, WIDTH + 30])
        else:
            self.x = choice([-30, WIDTH + 30, (WIDTH - offset) / 2])
        self.knocked = False
        self.frame = 1
        self.hp = 1
        self.dead = False
        self.speed = 0.5
        self.damage = 0.1

    def die(self):
        if not self.dead:
            dave.xp += 1
            self.frame = 1
        self.dead = True

    def update(self):

        if framecounter % 5 == 0:
            self.frame += 1
        if not self.dead:
            if self.frame > 4:
                self.frame = 1
            if self.frame < 5:
                self.image = f'bug{self.frame}'
            if self.x < (WIDTH - offset) / 2:
                self.x += self.speed
            elif self.x > (WIDTH - offset) / 2:
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
            if self.frame == 2:
                sounds.splat.play()
                self.frame += 1
            if self.frame < 6:
                self.image = f'bug_die{self.frame}'
            if self.frame > 15:
                enemies.remove(self)
        for tent in tents:
            if self.colliderect(tent):
                self.speed = 0
                if framecounter % 50 == 0:
                    tent.hp -= self.damage
        for building in envbuildings:
            if self.colliderect(building):
                if not self.dead:
                    if not building.building:
                        if framecounter % 500 == 0:
                            building.hp -= 1
                            break


class Wolf(Bug):
    def __init__(self):
        super().__init__()
        self.y = choice([randint(-60, -30), randint(HEIGHT + 20, HEIGHT + 60), HEIGHT / 2])
        if self.y == HEIGHT / 2:
            self.x = choice([randint(-60, -30), randint(WIDTH + 20, WIDTH + 60)])
        else:
            self.x = choice([randint(-60, -30), randint(WIDTH + 20, WIDTH + 60), (WIDTH - offset) / 2])
        self.image = 'wolf_wd_1'
        self.maxhp = 5
        if envbuildings:
            self.maxhp += len(envbuildings)
        self.hp = self.maxhp
        self.hit_time = None
        self.building_hit_time = None
        self.damage = 3
        self.knocked = False
        self.stucked = False

    def calc_knockback_coords(self, Mx, My, Cx, Cy, Mr):
        vector_x = Cx - Mx
        vector_y = Cy - My
        vector_length = math.sqrt((vector_x * vector_x) + (vector_y * vector_y))
        if vector_length == 0:
            vector_length = 0.1
        normalized_vector_x = vector_x / vector_length
        normalized_vector_y = vector_y / vector_length
        coords_x = Mx + normalized_vector_x * Mr
        coords_y = My + normalized_vector_y * Mr
        return [coords_x, coords_y]

    def update(self):

        if framecounter % 5 == 0:
            self.frame += 1
        if not self.dead:
            if self.frame > 5:
                self.frame = 1
            if self.frame < 6:
                self.image = f'wolf_wd_{self.frame}'

            if self.x < (WIDTH - offset) / 2:
                self.x += self.speed
            elif self.x > (WIDTH - offset) / 2:
                self.x -= self.speed
            if self.y < HEIGHT / 2:
                self.y += self.speed
            if self.y > HEIGHT / 2:
                self.y -= self.speed

            # LULOK animate(self, duration=20, tween='linear', pos=((WIDTH - offset) / 2, HEIGHT / 2))
        if self.hp <= 0:
            self.die()
        # for worker in workers:
        #     if self.colliderect(worker):
        #         pass
        if self.dead:

            if self.frame < 7:
                self.image = f'wolf_dead_{self.frame}'
            if self.frame == 1:
                sounds.wolfdie.play()
                self.frame += 1
            if self.frame > 15:
                dave.leather += 1
                enemies.remove(self)

        if self.knocked:
            x1, y1 = pygame.mouse.get_pos()
            knockback_pos = self.calc_knockback_coords(self.x, self.y, x1, y1, 120)
            animate(self, duration=0.4, pos=knockback_pos)
            self.speed = 0.5
            self.knocked = False
            # x1, y1 = self.pos
            # x2, y2 = dave.pos
            # distance = math.hypot(x1 - x2, y1 - y2)
            # if distance < 120:
            #     if self.x < dave.x:
            #         self.x -= 5
            #     else:
            #         self.x += 5
            #     if self.y < dave.y:
            #         self.y -= 5
            #     else:
            #         self.y += 5
            #     if self.colliderect(Tent()):
            #         self.stucked = True
            #     if self.colliderect(Barricade()):
            #         self.stucked = True
            #     if self.colliderect(Smalltower()):
            #         self.stucked = True
            # else:
            #     self.knocked = False
            #     self.speed = 0.5
        if self.stucked:
            self.x += 5
            self.y += 5
            if not self.colliderect(Tent()):
                self.stucked = False
            if not self.colliderect(Barricade()):
                self.stucked = False
            if not self.colliderect(Smalltower()):
                self.stucked = False
        if self.colliderect(dave):
            if not self.dead:
                if self.hit_time is None:
                    self.hit_time = pygame.time.get_ticks() / 1000
                    if dave.protected:
                        dave.in_hand.durability -= self.damage / 2
                    else:
                        dave.hp -= self.damage
                else:
                    if self.hit_time + 1 < pygame.time.get_ticks() / 1000:
                        if dave.protected:
                            dave.in_hand.durability -= self.damage / 2
                        else:
                            dave.hp -= self.damage
                        self.hit_time = pygame.time.get_ticks() / 1000
        for building in envbuildings:
            if self.colliderect(building):
                if not building.building:
                    self.speed = 0
                    if not self.dead:
                        if self.building_hit_time is None:
                            self.building_hit_time = pygame.time.get_ticks() / 1000
                            if not building.building:
                                building.hp -= self.damage / 2
                        else:
                            if self.building_hit_time + 1 < pygame.time.get_ticks() / 1000:
                                if not building.building:
                                    building.hp -= self.damage / 2
                                self.building_hit_time = pygame.time.get_ticks() / 1000
                else:
                    self.speed = 0.5
            else:
                self.speed = 0.5


class Gamestate(StateMachine):
    menuframe = 1
    mouse_holded = False
    gamestart_time = pygame.time.get_ticks() / 1000
    game_time = 0
    init = State('init', initial=True)
    menu = State('Menu')
    game = State('Game')
    help = State('Help')
    game_over = State('Game_over')
    gethelp = menu.to(help)
    start = init.to(menu)
    play = menu.to(game)
    lose = game.to(game_over)
    helpback = help.to(menu)
    gameoverback = game_over.to(menu)

    # def Buildingcollision(self, cls):
    #     if envbuildings:
    #         for bld in envbuildings:
    #             # if type(cls) != type(bld):
    #             if cls.colliderect(bld):
    #                 return True
    #                 break
    #             else:
    #                 return False

    def icon_hover(self, icon):
        mousepos = pygame.mouse.get_pos(2)
        if icons[icon].left < mousepos[0] < icons[icon].right:
            if icons[icon].top < mousepos[1] < icons[icon].bottom:
                return True
            else:
                return False

    def on_start(self):
        music.play('menusoundtrack')
        print('initmenu')
        self.mouseholded = False
        self.mouse_holded = False
        for k in range(0, 2):
            selectbars.append(Rect((WIDTH / 2 - 110 + (200 * k), HEIGHT / 3), (20, 50)))

        for d in range(0, 3):
            optionbars.append(Rect((WIDTH / 2 - 100, HEIGHT / 3 + (70 * d)), (200, 50)))

    def on_play(self):
        music.stop()
        music.play(choice(['gamesoundtrack1', 'gamesoundtrack2', 'gamesoundtrack3']))
        self.mouse_holded = False
        print('starting game')
        self.gamestart_time = pygame.time.get_ticks() / 1000
        pygame.mouse.set_cursor(pygame.cursors.broken_x)
        pygame.time.set_timer(USEREVENT, 0)
        dave.throwed_time = pygame.time.get_ticks() / 60
        if len(tents) < 1:
            tents.append(Tent())
            dave.wood = 0
            dave.grass = 0
            dave.stone = 0
            dave.leather = 0
            dave.xp = 0
            dave.hp = dave.maxhp
            envbuildings.clear()
            workers.clear()
            loot.clear()
            enemies.clear()
            hotbaritems.clear()
            dave.in_hand = None
            self.gamestart_time = pygame.time.get_ticks() / 1000

    def on_lose(self):
        self.mouse_holded = False
        buttonback.x = WIDTH / 2 - buttonback.width / 2
        buttonback.y = HEIGHT / 2 + 80
        selectbars[0].top = buttonback.top
        selectbars[0].x = buttonback.left
        selectbars[1].top = buttonback.top
        selectbars[1].x = buttonback.right

    def on_gameoverback(self):
        music.stop()
        music.play('menusoundtrack')
        self.mouse_holded = False
        for z in range(0, 2):
            selectbars[z].x = WIDTH / 2 - 110 + (200 * z)
            selectbars[z].y = HEIGHT / 3

    def on_gethelp(self):
        self.mouse_holded = False
        buttonback.x = WIDTH / 2 - 160
        buttonback.y = HEIGHT - 100
        selectbars[0].top = buttonback.top
        selectbars[0].x = buttonback.left
        selectbars[1].top = buttonback.top
        selectbars[1].x = buttonback.right

    def on_helpback(self):
        self.mouse_holded = False
        for x in range(0, 2):
            selectbars[x].x = WIDTH / 2 - 110 + (200 * x)
            selectbars[x].y = HEIGHT / 3

    def update(self):
        global mouse_holded
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

            elif keyboard.space:
                if not keypressed:
                    if selectbars[0].y == optionbars[0].y:
                        self.play()
                    if selectbars[0].y == optionbars[1].y:
                        self.gethelp()
                    if selectbars[0].y == optionbars[2].y:
                        exit()
                    keypressed = True
            else:
                keypressed = False
        if self.is_help:
            if keyboard.space:
                if not keypressed:
                    gmstate.helpback()
                    keypressed = True
            else:
                keypressed = False
        if self.is_game_over:
            if keyboard.space:
                if not keypressed:
                    gmstate.gameoverback()
                    keypressed = True
            else:
                keypressed = False

        if self.is_game:  ########################################## game update
            self.game_time = pygame.time.get_ticks() / 1000 - self.gamestart_time
            mousestate = pygame.mouse.get_pressed(3)
            mousepos = pygame.mouse.get_pos(2)
            if mousestate[0]:
                if not self.mouse_holded:
                    if self.icon_hover(0):
                        if icons[0].active:
                            if dave.leather >= 10:
                                if dave.wood >= 4:
                                    if dave.grass >= 8:
                                        if len(tents) < 2:
                                            for tent in tents:
                                                tent.x -= 30 * len(tents)
                                            tents.append(Tent())
                                            tents[-1].x += 30 * len(tents)
                                            dave.grass -= 8
                                            dave.wood -= 4
                                            dave.leather -= 10
                                            self.mouse_holded = True
                                        elif len(tents) < 3:
                                            # hard set coordinants lulok optimize
                                            for tent in tents:
                                                tent.x -= 30 * len(tents)
                                            tents.append(Tent())
                                            tents[-1].x += 30 * len(tents)
                                            workers[-1].pos = tents[-1].pos
                                            self.mouse_holded = True


                    elif self.icon_hover(1):
                        if dave.wood >= 8:
                            if dave.grass >= 4:
                                if len(envbuildings) != 0:
                                    if not envbuildings[-1].building:
                                        envbuildings.append(Barricade())
                                        dave.wood -= 8
                                        dave.grass -= 4
                                        self.mouse_holded = True
                                else:
                                    envbuildings.append(Barricade())
                                    dave.wood -= 8
                                    dave.grass -= 4
                                    self.mouse_holded = True

                    elif self.icon_hover(2):
                        towers_count = sum(1 for x in envbuildings if isinstance(x, Smalltower))
                        if dave.wood >= 10:
                            if dave.stone >= 10:
                                if dave.grass >= 4:
                                    if towers_count < len(workers) + 1:
                                        if len(envbuildings) != 0:
                                            if not envbuildings[-1].building:
                                                envbuildings.append(Smalltower())
                                                dave.wood -= 10
                                                dave.stone -= 10
                                                dave.grass -= 4
                                                self.mouse_holded = True
                                        else:
                                            envbuildings.append(Smalltower())
                                            dave.wood -= 10
                                            dave.stone -= 10
                                            dave.grass -= 4
                                            self.mouse_holded = True



                    elif self.icon_hover(3):
                        if dave.wood >= 2:
                            if dave.stone >= 1:
                                if dave.grass >= 2:
                                    if not dave.encumbered:
                                        hotbaritems.append(Spear())
                                        dave.wood -= 2
                                        dave.stone -= 1
                                        dave.grass -= 2
                                        self.mouse_holded = True
                                    else:
                                        screen.draw.text('You are Encumbered', (WIDTH / 2, 100), color='red')
                    elif self.icon_hover(4):
                        if dave.wood >= 4:
                            if dave.grass >= 4:
                                if not dave.encumbered:
                                    hotbaritems.append(Shield())
                                    dave.wood -= 4
                                    dave.grass -= 4
                                    self.mouse_holded = True
                                else:
                                    screen.draw.text('You are Encumbered', (WIDTH / 2, 100), color='red')
                    elif self.icon_hover(5):
                        if dave.leather >= 4:
                            if dave.grass >= 4:
                                for tent in tents:
                                    if dave.colliderect(tent):
                                        if not tent.hp == tent.maxhp:
                                            dave.wood -= 4
                                            dave.grass -= 4
                                            if tent.maxhp - tent.hp > 10:
                                                tent.hp += 10
                                            else:
                                                tent.hp = tent.maxhp
                                            sounds.tentrepair.play()
                                            self.mouse_holded = True
                                            break

            else:
                self.mouse_holded = False
            # icon0 availability
            if dave.leather >= 10:
                if dave.wood >= 4:
                    if dave.grass >= 8:
                        if len(tents) < 4:
                            icons[0].active = True
                        if len(tents) == 3:
                            icons[0].active = False

            else:
                icons[0].active = False

            # icon1
            if dave.wood >= 8 and dave.grass >= 4:
                icons[1].active = True
            else:
                icons[1].active = False

            towers_count = sum(1 for x in envbuildings if isinstance(x, Smalltower))

            if dave.wood >= 10 and dave.stone >= 10 and dave.grass >= 4:
                if towers_count < len(workers) + 1:
                    icons[2].active = True
                else:
                    icons[2].active = False
            else:
                icons[2].active = False

            if dave.wood >= 2 and dave.stone >= 1 and dave.grass >= 2:
                if not dave.encumbered:
                    for hotbar in hotbars:
                        if isinstance(hotbar, Hotbar):
                            if hotbar.occupied:
                                icons[3].active = False
                            else:
                                icons[3].active = True
                                break
                    else:
                        print('You have full hotbar')
            else:
                icons[3].active = False

            if dave.wood >= 4 and dave.grass >= 4:
                if not dave.encumbered:
                    for hotbar in hotbars:
                        if isinstance(hotbar, Hotbar):
                            if hotbar.occupied:
                                icons[4].active = False
                            else:
                                icons[4].active = True
                                break
                    else:
                        print('You have full hotbar')
            else:
                icons[4].active = False

            if dave.leather >= 4:
                if dave.grass >= 4:
                    if len(tents) < 4:
                        icons[5].active = True

            else:
                icons[5].active = False

            for idx, icon in enumerate(icons):
                if self.icon_hover(idx):
                    descbar.topright = mousepos
                if not icon.active:
                    inactiveicons[idx].pos = icons[idx].pos
                else:
                    inactiveicons[idx].pos = (-200, -200)

            for worker in workers:
                worker.update()
            for grass in grasses:
                grass.update()
            for item in loot:
                item.update()

            framecounter += 1
            if framecounter > 1000:
                framecounter = 0

            if gmstate.game_time > dave.wolftimer:
                enemies.append(Wolf())
                dave.wolftimer += 30 - (len(envbuildings) * 2.2)

            if gmstate.game_time > dave.wolfgrouptimer:
                if len(envbuildings) > 1:
                    for nbr in range(0, 3):
                        enemies.append(Wolf())
                    dave.wolfgrouptimer += 80 - (len(envbuildings) * 5)

            if dave.xp > 25:
                if framecounter % 1000 == 0:
                    if len(loot) < 10:
                        enemies.append(Wolf())

            if dave.xp > 45:
                if framecounter % 1000 == 0:
                        enemies.append(Wolf())

            if gmstate.game_time < 100:
                if framecounter % 1000 == 0:
                    enemies.append(Bug())

            if gmstate.game_time < 3:
                if framecounter % 100 == 0:
                    loot.append(Branch())
                    loot.append(Rock())

            if framecounter % 1000 == 0:
                if len(loot) < 10:
                    loot.append(Branch())
                    loot.append(Rock())
            dave.update()

            for bug in enemies:
                bug.update()
            for item in hotbaritems:
                item.update()
                if item.icon.pos == hotbars[-1].pos:
                    dave.in_hand = item

            for hotbar in hotbars:
                if isinstance(hotbar, Hotbar):
                    hotbar.update()
            for tent in tents:
                tent.update()

            for building in envbuildings:
                if isinstance(building, Smalltower):
                    if framecounter % 999 == 0:
                        enemies.append(Wolf())
                if building.building:
                    x1, y1 = building.pos
                    x2, y2 = dave.pos
                    distance = math.hypot(x1 - x2, y1 - y2)
                    actor_x.pos = building.pos
                    if distance < dave.buildingradius:
                        # if self.Buildingcollision(building):
                        # building.canplace = False
                        if 417 < mousepos[0] < 726 and 316 < mousepos[1] < 449:
                            building.canplace = False
                        # (417, 316)
                        # (726, 449)
                        else:
                            building.canplace = True
                    else:
                        building.canplace = False

                building.update()
            if dave.active_throwns:
                for thrown in dave.active_throwns:
                    thrown.update()

            if len(grasses) < 2:
                if framecounter % 880 == 0:
                    grasses.append(Grass())

            for idx, icon in enumerate(icons):
                if self.icon_hover(idx):
                    descbar.topright = mousepos

    def draw(self):
        mousepos = pygame.mouse.get_pos()
        if self.is_menu:
            screen.clear()
            screen.blit(pygame.image.load('images/menu-bg.png'), (0, 0))
            for optionbar in optionbars:
                screen.draw.filled_rect(optionbar, (100, 200, 100))
            for selectbar in selectbars:
                screen.draw.filled_rect(selectbar, (150, 250, 50))
            screen.draw.text('PLAY GAME', (WIDTH / 2 - 110 + 50, HEIGHT / 3 + 15), fontsize=30)
            screen.draw.text('HELP', (WIDTH / 2 - 110 + 80, HEIGHT / 3 + 85), fontsize=30)
            screen.draw.text('EXIT', (WIDTH / 2 - 110 + 80, HEIGHT / 3 + 155), fontsize=30)

            # if framecounter %100 == 0:
            #     self.menuframe += 1
            #     if self.menuframe > 3:
            #         self.menuframe = 1
            screen.draw.text('WILD CAMPERS', (WIDTH / 2 , 100), anchor=(0.5,0.5) ,fontsize=160)
            screen.blit(pygame.transform.scale(pygame.image.load(f'images/worker_idle_{self.menuframe}.png'), (60, 130)),(WIDTH / 4 , HEIGHT / 2))
            screen.blit(pygame.transform.scale(pygame.image.load(f'images/wildman_idle_{self.menuframe}.png'), (60, 130)),(WIDTH / 2 + 200, HEIGHT / 2))


        if self.is_help:
            screen.clear()
            screen.blit(pygame.image.load('images/bg-help.png'), (offset / 2, 0))
            screen.draw.filled_rect(buttonback, (100, 200, 100))
            screen.draw.filled_rect(selectbars[0], (150, 250, 50))
            screen.draw.filled_rect(selectbars[1], (150, 250, 50))
            screen.draw.text('BACK', (buttonback.x + buttonback.width / 2, buttonback.y + buttonback.height / 2),
                             anchor=(0.5, 0.5), fontsize=30)

        if self.is_game:
            screen.clear()
            background.draw()
            for bug in enemies:
                bug.draw()
                if isinstance(bug, Wolf):
                    if bug.hp < bug.maxhp:
                        screen.draw.filled_rect(
                            Rect((bug.left, bug.top - 8), (bug.maxhp * 3, 5)), (200, 0, 0))
                        screen.draw.filled_rect(
                            Rect((bug.left, bug.top - 8), (bug.hp * 3, 5)), (0, 200, 0))
            tree.draw()
            for grass in grasses:
                grass.draw()
            for build in envbuildings:
                if build.building:
                    if 417 < mousepos[0] < 726 and 316 < mousepos[1] < 449:
                        tentzone.draw()
                build.draw()
                if build.building:
                    screen.draw.circle(dave.pos, dave.buildingradius, (0, 50, 200))
                if build.type == 'tower':
                    for thrown in build.towerthrown:
                        thrown.draw()
                if not build.canplace:
                    actor_x.draw()
                if build.active:
                    if 0 < build.hp < build.maxhp:
                        if build.maxhp > 50:
                            screen.draw.filled_rect(
                                Rect((build.x - build.width / 4, build.y - 30), (build.maxhp / 2, 5)), (200, 0, 0))
                            screen.draw.filled_rect(Rect((build.x - build.width / 4, build.y - 30), (build.hp / 2, 5)),
                                                    (0, 200, 0))
                        else:
                            screen.draw.filled_rect(Rect((build.x - build.width / 4, build.y - 30), (build.maxhp, 5)),
                                                    (200, 0, 0))
                            screen.draw.filled_rect(Rect((build.x - build.width / 4, build.y - 30), (build.hp, 5)),
                                                    (0, 200, 0))
            stone.draw()
            for tent in tents:
                if tent.hp < tent.maxhp:
                    screen.draw.filled_rect(Rect((tent.left + tent.width / 2, tent.top - 10), (tent.maxhp, 5)),
                                            (200, 0, 0))
                    screen.draw.filled_rect(Rect((tent.left + tent.width / 2, tent.top - 10), (tent.hp, 5)),
                                            (0, 200, 0))
                    if tent.hp < 1:
                        tents.remove(tent)
                        break
                tent.draw()
            if len(tents) < 1:
                gmstate.lose()

            if hotbaritems:
                for item in hotbaritems:
                    if item.throwed:
                        item.draw()

            if dave.in_hand is not None:
                if isinstance(dave.in_hand, Shield):
                    if keyboard.w or keyboard.d:
                        dave.in_hand.draw()
                elif isinstance(dave.in_hand, Spear):
                    if keyboard.w or keyboard.a or keyboard.s:
                        dave.in_hand.draw()

            if not dave.dead:
                if dave.goingleft == True:
                    screen.blit(flip(dave._surf, True, False), dave.topleft)
                else:
                    dave.draw()

            if dave.in_hand is not None:
                if not keyboard.a and not keyboard.d and not keyboard.w and not keyboard.d:
                    dave.in_hand.draw()
                if isinstance(dave.in_hand, Shield):
                    if keyboard.a or keyboard.s:
                        dave.in_hand.draw()
                elif isinstance(dave.in_hand, Spear):
                    if keyboard.d:
                        dave.in_hand.draw()
            if workers != []:
                for worker in workers:
                    worker.draw()
                for grass in grasses:
                    if grass.colliderect(worker):
                        screen.draw.filled_rect(
                            Rect((grass.x - grass.width / 3, grass.y + grass.height / 2), (grass.maxwork, 5)),
                            (200, 200, 0))
                        screen.draw.filled_rect(
                            Rect((grass.x - grass.width / 3, grass.y + grass.height / 2), (grass.working_status, 5)),
                            (0, 0, 200))
            screen.blit(pygame.image.load('images/lista.png'), (1152, 0))
            for idx, icon in enumerate(icons):
                icon.draw()
                if inactiveicons[idx].pos == icon.pos:
                    inactiveicons[idx].draw()

            for item in loot:
                item.draw()

            for thrown in dave.active_throwns:
                thrown.draw()
            for grass in grasses:
                if grass.colliderect(dave):
                    screen.draw.filled_rect(
                        Rect((grass.x - grass.width / 3, grass.y + grass.height / 2), (grass.maxwork, 5)),
                        (200, 200, 0))
                    screen.draw.filled_rect(
                        Rect((grass.x - grass.width / 3, grass.y + grass.height / 2), (grass.working_status, 5)),
                        (0, 0, 200))
            # if dave.colliderect(Grass()):
            #     screen.draw.filled_rect(
            #         Rect((Grass().x - Grass().width / 3, Grass().y + Grass().height / 2), (Grass().maxwork, 5)), (200, 200, 0))
            #     screen.draw.filled_rect(
            #         Rect((Grass().x - Grass().width / 3, Grass().y + Grass().height / 2), (Grass().working_status, 5)),
            #         (0, 0, 200))
            if dave.hp < dave.maxhp:
                screen.draw.filled_rect(
                    Rect((dave.left, dave.top - 8), (dave.maxhp, 5)), (200, 0, 0))
                screen.draw.filled_rect(
                    Rect((dave.left, dave.top - 8), (dave.hp, 5)), (0, 200, 0))

            for hotbar in hotbars:
                hotbar.draw()
            for item in hotbaritems:
                item.icon.draw()
                if item.durability < item.maxdurability:
                    screen.draw.filled_rect(
                        Rect((item.icon.x - item.icon.width / 4, item.icon.y + item.icon.height / 3),
                             (item.maxdurability, 5)), (200, 0, 0))
                    screen.draw.filled_rect(
                        Rect((item.icon.x - item.icon.width / 4, item.icon.y + item.icon.height / 3),
                             (item.durability, 5)), (200, 200, 0))
            # icons help desc

            for idx, icon in enumerate(icons):
                if self.icon_hover(idx):
                    descbar.draw()
            if self.icon_hover(0):
                screen.draw.text('Tent', (descbar.x, descbar.top + 15), anchor=(0.5, 0.5), color='white')
                screen.draw.text('Build another tent. \n Expand your party.', (descbar.x, descbar.top + 36),
                                 anchor=(0.5, 0.5), color='black', fontsize=20)
                screen.draw.text('requirements:', (descbar.x, descbar.top + 70), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.blit(pygame.transform.scale(pygame.image.load('images/lumber.png'), (25, 25)),
                            (descbar.x - 50, descbar.top + 75))
                screen.draw.text(' x2', (descbar.x - 40, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/leather.png'), (25, 25)),
                            (descbar.x - 15, descbar.top + 75))
                screen.draw.text(' x10', (descbar.x - 5, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/grassfiber.png'), (25, 25)),
                            (descbar.x + 20, descbar.top + 75))
                screen.draw.text(' x8', (descbar.x + 30, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                if len(tents) == 3:
                    screen.draw.text('MAX TENTS COUNT', (descbar.x, descbar.bottom + 10), anchor=(0.5, 0.5),
                                     color='white',
                                     fontsize=25)

            if self.icon_hover(1):
                screen.draw.text('Barricade', (descbar.x, descbar.top + 15), anchor=(0.5, 0.5), color='white')
                screen.draw.text('Block your enemies', (descbar.x, descbar.top + 35), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.draw.text('right-click to rotate', (descbar.x, descbar.top + 50), anchor=(0.5, 0.5),
                                 color='black', fontsize=18)
                screen.draw.text('requirements:', (descbar.x, descbar.top + 70), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.blit(pygame.transform.scale(pygame.image.load('images/lumber.png'), (25, 25)),
                            (descbar.x - 45, descbar.top + 80))
                screen.draw.text(' x8', (descbar.x - 10, descbar.top + 95), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/grassfiber.png'), (25, 25)),
                            (descbar.x + 5, descbar.top + 80))
                screen.draw.text(' x4', (descbar.x + 40, descbar.top + 95), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                # screen.blit('lumber', (descbar.x, descbar.top + 80))
            if self.icon_hover(2):
                screen.draw.text('Tower', (descbar.x, descbar.top + 15), anchor=(0.5, 0.5), color='white')
                screen.draw.text('shoots rocks', (descbar.x, descbar.top + 30), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.draw.text('can\'t have more \n', (descbar.x, descbar.top + 50), anchor=(0.5, 0.5), color='black',
                                 fontsize=18)
                screen.draw.text('than people', (descbar.x, descbar.top + 53), anchor=(0.5, 0.5), color='black',
                                 fontsize=18)
                screen.draw.text('requirements:', (descbar.x, descbar.top + 70), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.blit(pygame.transform.scale(pygame.image.load('images/lumber.png'), (25, 25)),
                            (descbar.x - 50, descbar.top + 75))
                screen.draw.text(' x10', (descbar.x - 40, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/stones.png'), (25, 25)),
                            (descbar.x - 15, descbar.top + 75))
                screen.draw.text(' x10', (descbar.x - 5, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/grassfiber.png'), (25, 25)),
                            (descbar.x + 20, descbar.top + 75))
                screen.draw.text(' x4', (descbar.x + 30, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)

            if self.icon_hover(3):
                screen.draw.text('Spear', (descbar.x, descbar.top + 15), anchor=(0.5, 0.5), color='white')
                screen.draw.text('Aim behind target', (descbar.x, descbar.top + 30), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.draw.text('right-click to throw', (descbar.x, descbar.top + 45), anchor=(0.5, 0.5),
                                 color='black', fontsize=18)
                screen.draw.text('low durability', (descbar.x, descbar.top + 58), anchor=(0.5, 0.5), color='black',
                                 fontsize=18)
                screen.draw.text('requirements:', (descbar.x, descbar.top + 70), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.blit(pygame.transform.scale(pygame.image.load('images/lumber.png'), (25, 25)),
                            (descbar.x - 50, descbar.top + 75))
                screen.draw.text(' x2', (descbar.x - 40, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/stones.png'), (25, 25)),
                            (descbar.x - 15, descbar.top + 75))
                screen.draw.text(' x1', (descbar.x - 5, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/grassfiber.png'), (25, 25)),
                            (descbar.x + 20, descbar.top + 75))
                screen.draw.text(' x2', (descbar.x + 30, descbar.top + 110), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                if dave.encumbered:
                    screen.draw.text('HOTBARS FULL', (descbar.x, descbar.bottom + 10), anchor=(0.5, 0.5), color='white',
                                     fontsize=25)
            if self.icon_hover(4):
                screen.draw.text('Shield', (descbar.x, descbar.top + 15), anchor=(0.5, 0.5), color='white')
                screen.draw.text('Knock foes', (descbar.x, descbar.top + 30), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.draw.text('in right-click', (descbar.x, descbar.top + 45), anchor=(0.5, 0.5), color='black',
                                 fontsize=18)
                screen.draw.text('direction', (descbar.x, descbar.top + 58), anchor=(0.5, 0.5), color='black',
                                 fontsize=18)
                screen.draw.text('requirements:', (descbar.x, descbar.top + 70), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                if dave.encumbered:
                    screen.draw.text('HOTBARS FULL', (descbar.x, descbar.bottom + 10), anchor=(0.5, 0.5), color='white',
                                     fontsize=25)
                screen.blit(pygame.transform.scale(pygame.image.load('images/lumber.png'), (25, 25)),
                            (descbar.x - 45, descbar.top + 80))
                screen.draw.text(' x4', (descbar.x - 10, descbar.top + 95), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/grassfiber.png'), (25, 25)),
                            (descbar.x + 5, descbar.top + 80))
                screen.draw.text(' x4', (descbar.x + 40, descbar.top + 95), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
            if self.icon_hover(5):
                screen.draw.text('Repair TENT', (descbar.x, descbar.top + 15), anchor=(0.5, 0.5), color='black')
                screen.draw.text('use near tent', (descbar.x, descbar.top + 30), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.draw.text('walk to it if not works', (descbar.x, descbar.top + 45), anchor=(0.5, 0.5), color='black',
                                 fontsize=18)
                screen.draw.text('requirements:', (descbar.x, descbar.top + 60), anchor=(0.5, 0.5), color='black',
                                 fontsize=20)
                screen.blit(pygame.transform.scale(pygame.image.load('images/leather.png'), (25, 25)),
                            (descbar.x - 45, descbar.top + 80))
                screen.draw.text(' x4', (descbar.x - 10, descbar.top + 95), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)
                screen.blit(pygame.transform.scale(pygame.image.load('images/grassfiber.png'), (25, 25)),
                            (descbar.x + 5, descbar.top + 80))
                screen.draw.text(' x4', (descbar.x + 40, descbar.top + 95), anchor=(0.5, 0.5), color='black',
                                 fontsize=24)

            # screen.draw.filled_rect(Rect((WIDTH - 60, 10), (50, 200)), (200, 200, 0))
            screen.blit('lumber', (WIDTH - 80, 10))
            screen.draw.text(f' x {dave.wood}', (WIDTH - 50, 20), color='black')
            screen.blit('stones', (WIDTH - 80, 50))
            screen.draw.text(f' x {dave.stone}', (WIDTH - 50, 55), color='black')
            screen.blit('grassfiber', (WIDTH - 80, 80))
            screen.draw.text(f' x {dave.grass}', (WIDTH - 50, 88), color='black')
            screen.blit('leather', (WIDTH - 80, 115))
            screen.draw.text(f' x {dave.leather}', (WIDTH - 50, 120), color='black')

            screen.draw.text(f'XP: {dave.xp}', (WIDTH - 50, HEIGHT - 100), anchor=(0.5, 0.5), color='black')

        if self.is_game_over:
            screen.clear()
            screen.draw.text(f'GAME OVER', (WIDTH / 2, HEIGHT / 2 - 120), anchor=(0.5, 0.5), color='white', fontsize=50)
            screen.draw.text(f'Score: {dave.xp}', (WIDTH / 2, HEIGHT / 2 - 80), anchor=(0.5, 0.5), color='white')
            screen.draw.filled_rect(buttonback, (100, 200, 100))
            screen.draw.text('BACK', (buttonback.x + buttonback.width / 2, buttonback.y + buttonback.height / 2),
                             anchor=(0.5, 0.5), fontsize=30)
            screen.draw.filled_rect(selectbars[0], (150, 250, 50))
            screen.draw.filled_rect(selectbars[1], (150, 250, 50))


gmstate = Gamestate()
enemies.append(Bug())
tents.append(Tent())
dave = Dave()
actor_x = Actor('actor_x')
tentzone = Actor('tentzone')
tentzone.topleft = (417, 316)
tree = Tree()
stone = Stone()
grasses.append(Grass())
descbar = Actor('descriptionbar')

hotbars = []
for i in range(0, 8):
    thislen = len(hotbars)
    hotbars.append(Hotbar())
    hotbars[-1].bottom = HEIGHT - 10
    if thislen < 1:
        hotbars[-1].left = WIDTH / 3
    else:
        hotbars[-1].left = hotbars[thislen - 1].right + 5
hotbars.append(ActiveHotbar())
hotbars[-1].pos = hotbars[0].pos

# build icons
icons.append(Icon())
icons[-1].pos = (WIDTH - 2 * icons[-1].width - 8, 324)
icons.append(Icon())
icons[-1].left = icons[len(icons) - 2].right + 8
icons[-1].y = icons[len(icons) - 2].y
icons.append(Icon())
icons[-1].top = icons[0].bottom + 10
icons[-1].x = icons[0].x

# craft icons

icons.append(Icon())
icons[-1].top = icons[0].bottom + 126
icons[-1].x = icons[0].x

icons.append(Icon())
icons[-1].top = icons[0].bottom + 126
icons[-1].left = icons[len(icons) - 2].right + 8

icons.append(Icon())
icons[-1].top = icons[len(icons) - 3].bottom + 10
icons[-1].x = icons[len(icons) - 3].x

inactiveicons = []
for icon in icons:
    inactiveicons.append(Actor('inactive_icon'))


def on_mouse_down(pos, button):
    # print("Mouse button", button, "clicked at", pos)
    if gmstate.is_game_over:
        if button == mouse.LEFT:
            if not gmstate.mouse_holded:
                if buttonback.left < pos[0] < buttonback.right:
                    if buttonback.top < pos[1] < buttonback.bottom:
                        gmstate.mouse_holded = True
                        gmstate.gameoverback()

    if gmstate.is_help:
        if button == mouse.LEFT:
            if not gmstate.mouse_holded:
                if buttonback.left < pos[0] < buttonback.right:
                    if buttonback.top < pos[1] < buttonback.bottom:
                        gmstate.mouse_holded = True
                        gmstate.helpback()
    if gmstate.is_menu:
        if button == mouse.LEFT:
            if not gmstate.mouse_holded:
                if optionbars[0].left < pos[0] < optionbars[0].right:
                    if optionbars[0].top < pos[1] < optionbars[0].bottom:
                        gmstate.mouse_holded = True
                        gmstate.play()
                if optionbars[1].left < pos[0] < optionbars[1].right:
                    if optionbars[1].top < pos[1] < optionbars[1].bottom:
                        gmstate.mouse_holded = True
                        gmstate.gethelp()
                if optionbars[2].left < pos[0] < optionbars[2].right:
                    if optionbars[2].top < pos[1] < optionbars[2].bottom:
                        gmstate.mouse_holded = True
                        quit()
    if gmstate.is_game:
        if button == mouse.WHEEL_UP:
            dave.hotbar -= 1
            if dave.hotbar < 0:
                dave.hotbar = 0
            hotbars[-1].pos = hotbars[dave.hotbar].pos
        elif button == mouse.WHEEL_DOWN:
            dave.hotbar += 1
            if dave.hotbar > 7:
                dave.hotbar = 7
            hotbars[-1].pos = hotbars[dave.hotbar].pos

        if button == mouse.RIGHT:

            for item in hotbaritems:
                if item.in_hand:
                    if isinstance(item, Spear):
                        if len(envbuildings) != 0:
                            if not envbuildings[-1].building:
                                item.Throw()
                        else:
                            item.Throw()


def update():
    gmstate.update()


def draw():
    gmstate.draw()


def init_game():
    global background
    level = pytmx.TiledMap('maps/map1.tmx')
    # layer = level.get_layer_by_name('actors')
    bglayer = level.get_layer_by_name('background')
    image = Path(bglayer.image[0])
    background = Actor(image.stem)


init_game()
pgzrun.go()
