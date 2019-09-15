import pygame
import json


class Action:
    def __init__(self, obj, func, *args, t=0, max_t=None):
        self.func = func
        self.t = t
        self.max_t = max_t
        self.args = args
        self.obj = obj

    def update(self):
        self.t += 1
        if self.max_t is not None and self.t > self.max_t:
            self.obj.actions.remove(self)
        self.func(self.obj, self.t, *self.args)

    @staticmethod
    def drop_action(obj, t, g, first_pos, first_speed):
        obj.speed[1] = first_speed - g * t
        obj.pos[1] = first_pos + first_speed * t - g * t ** 2


class Settings:
    const = json.load(open('constants', 'r'))
    SCR_SIZE = const['SCR_SIZE']
    ABS_SIZE = const['ABS_SIZE']
    scale = SCR_SIZE[0] / ABS_SIZE[0]


def scale(a):
    if isinstance(a, (tuple, list)):
        return type(a)([i * Settings.scale for i in a])
    return a * Settings.scale


class ListMethods:
    @staticmethod
    def add(a, b):  # ++
        return [a[0] + b[0], a[1] + b[1]]

    @staticmethod
    def s_a(a, b):  # -+
        return [a[0] - b[0], a[1] + b[1]]

    @staticmethod
    def a_s(a, b):  # +-
        return [a[0] + b[0], a[1] - b[1]]

    @staticmethod
    def sub(a, b):  # --
        return [a[0] - b[0], a[1] - b[1]]

    @staticmethod
    def mul(a, b):  # *
        return [a[0] * b[0], a[1] * b[1]]


class HitBox(pygame.sprite.Group):
    def __init__(self, size, pos=None):
        super().__init__()
        self.max_pos = [0, 0]
        self.size = size
        self.pos = [0, 0] if pos is None else pos
        self.draw_list = []
        self.actions = set()

    def add_sprite(self, sprite):
        if sprite not in self.draw_list:
            self.draw_list.append(sprite)

    def del_sprite(self, sprite):
        if sprite in self.draw_list:
            self.draw_list.remove(sprite)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == 'pos':
            self.max_pos = ListMethods.add(self.pos, self.size)

    def check_touch(self, other):
        return not (self.max_pos[0] < other.pos[0] or self.pos[0] > other.max_pos[0] or
                    self.max_pos[1] < other.pos[1] or self.pos[1] > other.max_pos[1])

    def draw(self, surface: pygame.Surface):
        for sp in self.draw_list:
            sp.draw(surface)

    def update(self, *args):
        for action in self.actions:
            action.update()
        for sp in self.draw_list:
            sp.update(*args)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, name: str, pos, parent=(0, 0)):
        super().__init__()
        self.name = name
        self.plus_pos = pos
        self.parent = parent

    def draw(self, screen: pygame.Surface):
        pos = self.parent.pos if isinstance(self.parent, HitBox) else self.parent
        screen.blit(Globals.images[self.name], ListMethods.add(pos, self.plus_pos))
        print('draw')


def to_int(a):
    if isinstance(a, (tuple, list)):
        return type(a)([int(i) for i in a])
    return int(a)


class Globals:
    screen = pygame.display.set_mode(Settings.SCR_SIZE)
    timer = pygame.time.Clock()
    pygame.init()

    img_info: dict = json.load(open('sprites/poses', 'r'))
    img_sets: dict = json.load(open('settings', 'r'))
    images = {}  # to draw
    hitboxes = {}  # to touch

    @staticmethod
    def init_imgs():

        def load_img(name, size, img_info, images):
            size = to_int(ListMethods.mul(img_info[name]['size'], size))
            images[name] = pygame.transform.scale(pygame.image.load(f'sprites/{name}.png'), size)

        for name in Globals.img_sets.keys():
            if isinstance(Globals.img_sets[name], dict):
                sets = Globals.img_sets[name]
                hitbox = HitBox(sets['size'])
                size = scale(sets['size'])
                for part in sets['parts']:
                    n_name = f'{name}-{part}'
                    load_img(n_name, size, Globals.img_info, Globals.images)
                    hitbox.add(Sprite(n_name, ListMethods.mul(Globals.img_info[n_name]['pos'], size), hitbox))
                for part in sets['other']:
                    n_name = f'{name}-{part}'
                    load_img(n_name, size, Globals.img_info, Globals.images)
                    hitbox.add_sprite(Sprite(n_name, ListMethods.mul(Globals.img_info[n_name]['pos'], size), hitbox))
                Globals.hitboxes[name] = hitbox
            else:
                size = Globals.img_sets[name]
                load_img(name, size, Globals.img_info, Globals.images)

    draw_group = pygame.sprite.Group()

    platforms = set()


class Player(HitBox):  # !
    def __init__(self):
        size = Globals.hitboxes['player'].size
        super().__init__(size, [Settings.SCR_SIZE[0] / 2, Settings.SCR_SIZE[1] / 2])
        self.speed = [scale(20), 0]
        self.touch_checks = {}
        self.jump()
        Globals.hitboxes['player'] = self

    def jump(self):
        self.actions.add(Action(self, Action.drop_action, 0.1, self.pos, self.speed))

    def update(self, *args):
        # a = (self.speed[1] <= 0)
        a = self.pos[1]

        super().update(*args)

        if self.speed[1] <= 0:
            # for platform in Globals.platforms:
            #     if not a and self.max_pos < platform.max_pos[1]:
            #         self.touch_checks[platform] =
            for platform in Globals.platforms:
                if platform.check_touch(self) and a < platform.pos[0]:
                    self.jump()
                    break

    def draw(self, *args):
        super().draw(*args)
        print('draw!')


class Platform(HitBox):  # !
    def __init__(self, size_x, pos):
        super().__init__([size_x, 0], pos)

    def check_touch(self, other):
        return not (self.pos[1] > other.max_pos[1] or self.pos[1] < other.pos[1] or
                    self.pos[0] > other.max_pos[0] or self.max_pos[0] < other.pos[0])


class Enemy(HitBox):
    pass
