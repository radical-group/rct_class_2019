import sys
import time
import argparse
import pickle
import example_compute

class pythonExecutor(object):
    e_engine = "eval"
    function = None
    params = None
    resources = None

    def set_argument(self):
        parser = argparse.ArgumentParser("Python function executor")
        parser.add_argument("--function", help="func name")
        parser.add_argument("--params", nargs="+", help="params", default="")
        args = parser.parse_args()
        self.args = args
        self.function = args.function
        self.params = args.params
        if args.function is None:
            parser.print_usage()
            sys.exit()

    def executor(self):
        func = getattr(self, "magic_execute_{}".format(self.e_engine))
        return func()

    def magic_execute_eval(self):
        params =  self.params
        if isinstance(self.params, list):
            params = [ str (x) for x in self.params ]
        sep = self.function.split(".", 1)
        function = self.function
        if len(sep) > 1:
            module = __import__(sep[0])
            function = "{}.{}".format("module", sep[1])
        cmd = "{}({})".format(function, ",".join(params))
        return eval(cmd)

    def magic_execute_exec(self):
        cmd = "{}({})".format(self.function, ",".join(self.params))
        exec("res={}".format(cmd))
        return res

    def magic_execute_pickle(self):
        od1 = pickle.dumps(self.function)
        return od1(self.params)

if __name__ == "__main__":

    obj = pythonExecutor()
    obj.set_argument()
    res = obj.executor()
    print ("result: {} of function ({})".format(res, obj.function))

