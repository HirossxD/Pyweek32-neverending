import pgzero
import pygame
import pytmx
import pgzrun
from config import TITLE, WIDTH, HEIGHT
from statemachine import StateMachine, State
from pgzero.actor import Actor
from pgzero.keyboard import keyboard


class Gamestate(StateMachine):
    menu = State('Menu', initial=True)
    game = State('Game')

    play = menu.to(game)
    def update(self):
        if self.is_menu:
            if keyboard.space:
                self.play()
gmstate = Gamestate()

def update():
    gmstate.update()
    print(gmstate.current_state)


def draw():
    pass


pgzrun.go()
