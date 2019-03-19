class Unit:
    def __init__(self, func, args=tuple(), kwargs=dict()):
        self.func   = func
        self.args   = args
        self.kwargs = kwargs

    def call(self):
        return '{func}(*{args}, **{kwargs})'.format(func=self.func, args=self.args, kwargs=self.kwargs)
