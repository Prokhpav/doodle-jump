import pygame
import json
from typing import List, Dict


class Settings:
    data_way = 'data/'

    __dict__ = json.load(open(data_way + 'constants', 'r'))

    SCR_SIZE = __dict__['SCR_SIZE']
    ABS_SIZE = __dict__['ABS_SIZE']

    scale = SCR_SIZE[0] / ABS_SIZE[0]


def list_func(func, *lists):
    return lists[0].__class__([func(*i) for i in zip(*lists)])


funcs = {
    'scale': lambda x: x * Settings.scale,
    'int_sc': lambda x: int(x * Settings.scale),
    'add': lambda x, y: x + y,
    'sub': lambda x, y: x - y,
    'mul': lambda x, y: x * y,
    'div': lambda x, y: x / y}


def scale(a):
    try:
        return list_func(funcs['scale'], a)
    except TypeError:
        return a * Settings.scale


class Node:
    def copy_to(self, other):
        other.pos = self.pos
        other.rect = self.rect
        other.truepos = self.pos
        other.actions = self.actions

    def __init__(self, pos, size):
        if pos is None:
            return
        self.pos = [0, 0]
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.truepos = pos
        self.actions = set()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in ('pos', 'truepos') and hasattr(self, 'rect'):
            self.rect.topleft = list_func(funcs['add'], self.pos, self.truepos)

    def update(self, *args):
        for action in self.actions:
            action.update()

    def draw(self, surface: pygame.Surface):
        pass


class Sprite(Node):
    def copy_to(self, other):
        super().copy_to(other)
        other.image = super().__getattribute__('image')

    def __init__(self, name, pos, size, visible=True):
        super().__init__(pos, size)
        self.visible = visible
        self.image = name

    def __getattribute__(self, item):
        if item == 'image':
            return Globals.images[super().__getattribute__('image')]
        return super().__getattribute__(item)

    def draw(self, surface: pygame.Surface):
        if self.visible:
            surface.blit(self.image, self.rect)


class Group(Node):  # ?
    def copy_to(self, other):
        super().copy_to(other)
        other.sprites = self.sprites

    def __init__(self, pos, size):
        if pos is None:
            return
        super().__init__(pos, size)
        self.sprites: List[Sprite] = []

    def add(self, sprite):
        self.sprites.append(sprite)

    def kill(self, sprite):
        self.sprites.remove(sprite)

    def draw(self, surface: pygame.Surface):
        for spr in self.sprites:
            pos = spr.pos
            spr.pos = list_func(funcs['add'], pos, self.pos)
            spr.draw(surface)
            spr.pos = pos

    def update(self, *args):
        super().update(*args)
        for spr in self.sprites:
            spr.update(*args)


class Globals:
    screen = pygame.display.set_mode(Settings.SCR_SIZE)
    timer = pygame.time.Clock()
    pygame.init()

    img_poses: Dict[str, dict] = json.load(open(Settings.data_way + 'poses', 'r'))
    img_sizes: Dict[str, list] = json.load(open(Settings.data_way + 'settings-2', 'r'))
    images: Dict[str, pygame.sprite.Sprite] = {}  # to draw
    groups: Dict[str, Group] = {}  # to draw
    sprites: Dict[str, Sprite] = {}  # to draw

    draw_group = Group([0, 0], Settings.SCR_SIZE)


def load_image(name, size, pos, visible=True):
    surface = pygame.transform.scale(pygame.image.load(f'{Settings.data_way}sprites/{name}.png'),
                                     list_func(funcs['int_sc'], size))
    Globals.images[name] = surface
    Globals.sprites[name] = Sprite(name, pos, size, visible)


def init_images():
    def mul(a, b):
        return [a[0] * b[0], a[1] * b[1]]

    sizes = Globals.img_sizes
    for name in Globals.img_poses:
        group = (name.split('-')[0] if '-' in name else name)
        poses = Globals.img_poses[name]
        pos_ = mul(sizes[group], poses['pos'])
        size = mul(sizes[group], poses['size'])
        if name.endswith('*'):
            name = name[:-1]
            visible = False
        else:
            visible = True
        load_image(name, size, pos_, visible)
        if '-' in name:
            if group not in Globals.groups:
                size = list_func(funcs['int_sc'], sizes[group])
                Globals.groups[group] = Group([0, 0], size)
            Globals.groups[group].add(Globals.sprites[name])


init_images()
