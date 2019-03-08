from executor import PythonExecutor

if __name__ == "__main__":

    obj = PythonExecutor()
    obj.set_argument()
    res = obj.executor()
    print ("Function ({}) return value: {}".format(obj.function, res))

