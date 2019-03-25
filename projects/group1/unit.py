class Unit:
    def __init__(self, code, args=tuple(), kwargs=dict()):
        self.code   = code
        self.args   = args
        self.kwargs = kwargs

    def call_eval(self):
        return '{code}(*{args}, **{kwargs})'.format(code=self.code, args=self.args, kwargs=self.kwargs)

    def call_exec(self):
        return self.code

    def call(self):
        #TODO: remove from calls later
        return self.call_exec()