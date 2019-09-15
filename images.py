from all_images import *
import pygame


class Globals(Globals):
    platforms = []
    gravity = scale(0.6)
    player_jsp = scale(-25)
    pass


class Platform(Node):
    pass


class Player(Group):
    def __init__(self, groupname='player', pos=(0, 0)):
        super().__init__(None, None)
        group = Globals.groups[groupname]
        group.copy_to(self)
        Globals.groups[groupname] = self
        self.pos = pos

    def jump(self):
        self.actions.add(Action(self, ActFunc.accelerate, Globals.gravity, self.pos.copy(), Globals.player_jsp, 1))
        print('j', self.pos[1])

    def update(self, *args):
        super().update(*args)
        if self.pos[1] >= Settings.SCR_SIZE[1]:
            self.actions.clear()
            self.jump()
