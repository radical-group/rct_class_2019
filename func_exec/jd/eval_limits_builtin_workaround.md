* The `eval()` function will only accept an expression

* We can still import modules and use them, with the builtin function `__import__`. 
This succeeds:

`eval("__import__('os').system('clear')", {})`

In the case of `import time`: 

`eval("__import__('time')", {})`

* output: 

```
<module 'time' from '/usr/local/Cellar/python/2.7.12_2/Frameworks/Python.framework/Versions/2.7/lib/python2.7/lib-dynload/time.so'>
```

or use the import_module() function:

```
>>> import importlib
>>> eval("importlib.import_module('os')")
<module 'os' from '/usr/lib/python3.4/os.py'>

```
Safety: 

* Given the builtin function of `__import__` we can do potentially dangerous
things like: `eval("__import__('os').system('rm -fr /')", {'__builtins__':{}})`

https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
