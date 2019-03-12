import os
import sys
import time
import argparse
import pickle
import example_compute
import logging
from datetime import datetime
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class PythonExecutor(object):
    """Executes a Python function from parsing user string

    Attributes:
        e_engine: Executor method, eval() is default
        function: String of a function descriptor
        params: Function parameters to feed
    """

    e_engine = "eval"
    

    def __init__(self, function=None, params=None):
        self.function = function
        self.params = params

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
        func = getattr(self, "_magic_execute_{}".format(self.e_engine))
        return func()

    def _magic_execute_eval(self):
        params =  self.params
        if isinstance(self.params, list):
            params = [ str (x) for x in self.params ]
        sep = self.function.split(".", 1)
        function = self.function
        if len(sep) > 1:
            module = __import__(sep[0])
            function = "{}.{}".format("module", sep[1])
        cmd = "{}({})".format(function, ",".join(params))
        #logging.debug("eval:{}({})".format(self.function, ",".join(params)))
        return eval(cmd)

    def _magic_execute_exec(self):
        cmd = "{}({})".format(self.function, ",".join(self.params))
        exec("res={}".format(cmd))
        return res

    def _magic_execute_pickle(self):
        od1 = pickle.dumps(self.function)
        return od1(self.params)



def function_executor(work):
    """Executes a parameter using PythonExecutor

    Args:
        work (dict): a Task dictionary with 'function' and 'params' required
        keys

    Returns:
        A dictionary with a return value of a function
    """

    pe = PythonExecutor(function=work['function'],params=work['params'])
    result = { 
            'pid': os.getpid(), 
            # 'executed': str(datetime.now()), 
            'executed' : str(time.time()),
            # 'result': pe.executor(),
            'result' : str(time.time()),
            # 'completed': str(datetime.now()) 
            'completed' : str(time.time())}
    return { **result, **work } 



