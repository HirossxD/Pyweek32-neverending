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
WIDTH = 800
HEIGHT = 400

pos_hotbar = 0
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


def update():
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                print(event)
                pos_hotbar += 1
                hotbars[-1].pos = hotbars[dave.hotbar].pos
            elif event.button == 5:
                pos_hotbar -= 1
                hotbars[-1].pos = hotbars[dave.hotbar].pos
def draw():
    screen.clear()
    screen.fill('blue')
    for hotbar in hotbars:
        hotbar.draw()

pgzrun.go()