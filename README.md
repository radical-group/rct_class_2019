# rct_class_2019


## Func Executor

This exercise is supposed to move us toward a Python function executor.  To get there, the first step is to learn how to execute Python functions.  The simple approach:

```
def run_time():
    return time.time()

def run_sleep(arg):
    return time.sleep(arg)

def executor(cud):
    if cud['executable'] == 'time': run_time()
    if cud['executable'] == 'sleep': run_sleep(cud['arguments'])
```

won't cut it, because then we are limited to methods which are hard coded in our executor.  Instead we need to be able to do something like this:

```
def executor(cud):
    function_and_args = "%s(%s)" % (cud['executable'], ','.join(cud['arguments'])
    return magic_execute(function_and_args)
```

which would then should work for this compute unit description:

```
   {'executable' : 'time.sleep',
    'arguments' : [1]}
```

