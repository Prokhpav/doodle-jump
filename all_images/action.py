class ActFunc:
    @staticmethod
    def accelerate(obj, t, acc, pos, speed, i=0):
        now_speed = speed + acc * t
        obj.pos[i] = pos[i] + (speed + now_speed) * t / 2


class Action:
    def __init__(self, obj, func, *args, start=0, stop=None, **kwargs):
        # func: def a(obj, t, g, f_sp, ...):
        #             obj.pos = f_sp + g * t ** 2 / 2 ...
        self.obj = obj
        self.func = func
        self.t = start
        self.stop = stop
        self.akw = [args, kwargs]
        self.obj.actions.add(self)

    def update(self):
        self.t += 1
        if self.stop is not None and self.t >= self.stop:
            self.obj.actions.remove(self)
        self.func(self.obj, self.t, *self.akw[0], **self.akw[1])
