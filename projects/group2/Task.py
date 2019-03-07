class Task:

    def __init__(self, function = None, params = None, resources = None):
            self.function = function
            self.params = params
            self.resources = resources

    def __repr__(self):
            return repr((self.function, self.params, self.resources))
