In addition to the limitations of exec and eval discussed last class (security, potentially difficult to debug, potentially cumbersome with imports, etc.) there
are some more things that warrant discussion:

* `eval()`

Eval interprets strings as code and _returns a value_
However it _cannot_ execute functions inside of it.
As a trivial example:

```
>>> a = 'print(24)'
>>> eval(a)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1
    print(24)
        ^
SyntaxError: invalid syntax
```

It is very likely that our usecases might need us to use
python functions such as `print`, `sort`, `try/except` etc., and in those cases the usefulness of `eval()` is limited.

You can wrap eval calls with try/except statements
```
try:
  eval(a)
except SyntaxError as e:
  # handle error
  pass
except Exception as e:
  # handle error
  pass
```

A limitation of `eval()` that it needs to be fed a single expression/single line of code.


* `exec()`:

`exec()` also interprets string as code, but does not return a value.
It can execute functions within it.

```
>>> exec(a)
24

```

However it does not _return_ anything:

```
>>> a = '5+9'
>>> eval(a)
14
>>> exec(a)
>>>

```
`exec()` seems to be able to accept larger blocks of code, like so:

```
lines = 'a=1\nb=2\nc=a+b\nprint("c =",c)'

```

The code inside exec is is able to access the scope outside the code string
```
>>> outside_var = 'world'
>>> exec('print("hello " + outside_var)')
hello world

```

You can also define variables inside of exec that can be accessed outside of it.
This is dangerous because it can change the definitions of variables that inside each unit handler.
```
>>> exec('exec_var = "Hey, I am initiated inside exec"')
>>> exec_var
'Hey, I am initiated inside exec'

```


If we want our python method to return an object, `exec()` cannot deliver.

* `compile()`

`compile()` is basically a 2 step exec/eval. It just converts the string to a python code but does not execute.
It must then be run with `exec()` or `eval()`.


What we use between the two would depend on what we want out of it.



