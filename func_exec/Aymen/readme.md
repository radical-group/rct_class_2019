# Simple Socket client-Server python executor.

## Steps to run it :
  
1. Open 2 terminals .
2. Modify the cud dict in the client_exe.py with :
    - Module     : ```python modules ```  
    - Executable : ```python function``` ,```executable *.py``` etc.
    - Arguments  : ```any args that your code will take ```
3. Terminal number 1 do:  ``` python server_exe.py ```
4. Terminal number 2 do: ```  python client_exe.py ```
5. If everything is correct you should see results back in your client terminal.


what are the limitations of `eval` ?

I think it depend on the case that we are trying to solve. But one of the important thigs that i noticed is the ```eval``` in ``` python 2 ``` and ```python 3 ``` is : 
```
Python3

def aa():

    canBusType = 'CANdiag'
    result = [eval('canBusType') for i in range(3)]
    print (result)
    
   error : NameError: name 'canBusType' is not defined


Python2

def aa():

    canBusType = 'CANdiag'
    result = [eval('canBusType') for i in range(3)]
    print (result)
    
  output :  ['CANdiag', 'CANdiag', 'CANdiag']

```

## Explination of this problem :
This is expected, and won't easily fix.  The reason is that list
comprehensions in 3.x use a function namespace "under the hood" (in 2.x,
they were implemented like a simple for loop). Because inner functions
need to know what names to get from what enclosing namespace, the names
referenced in eval() can't come from enclosing functions. They must
either be locals or globals.

### source : https://bugs.python.org/issue5242


### RCT Class Assignemnt.
## what are the differences between eval() and exec()

Eval() : used to evalute single expression of python that generated dynamicaly example on that:

      ```
      >>> Num = 2
      >>> calc = '42 * Num'
      >>> res = eval(calc)
      >>> res
          84 
      ```     
          
If we want to execute or evalute long expression that can contain ``` try ``` ,``` def ``` etc... example :

       ```
       >>> def aa(arg):
                   {
                   print("Called with %d" % arg)
                   return arg * 8
                   }         
       >>> eval (aa(10))
       >>> Called with 10 
       >>> 80
      
       >>> exec (aa(10))
       >>> Called with 10 
       
       ```
  The code above indicates that eval can return value and exec can not .
  
  # Also ....
  
  What you cannot do in Pythons 2.7-3.6 with its compatibility hack, is to store the return value of ``exec`` into a variable:
  
    ``
    Python 2.7
    Type "help", "copyright", "credits" or "license" for more information.
    >>> a = exec('print(42)')
    File "<stdin>", line 1
    a = exec('print(42)')
           ^
    SyntaxError: invalid syntax
    ``
  # But what we can do to solve this is combining compile, eval and exec.
  
     
     std = eval(compile(cmd, '<string>', 'eval')) 
     
     or 
 
     std = eval(compile(cmd, '<string>', 'exec')) 
     
 
   The limitation of combining eval with compile or exec comes from the actual python interpreter version example
   (Another Python2/Python3 bug):

   A source fragment containing 2 top-level statements is an error for the 'single', except in Python 2 there is a bug that sometimes      allows multiple toplevel statements in the code; only the first is compiled; the rest are ignored:
     
 
   
     In Python 2.7.8:

     >>> exec(compile('a = 5\na = 6', '<string>', 'single'))
     >>> a
         5
   
     And in Python 3.4.2:
    

    >>> exec(compile('a = 5\na = 6', '<string>', 'single'))
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "<string>", line 1
    a = 5
            ^
    SyntaxError: multiple statements found while compiling a single statement
 
### Source  https://stackoverflow.com/questions/2220699/whats-the-difference-between-eval-exec-and-compile
    
