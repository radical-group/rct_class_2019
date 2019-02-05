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

I think it depend on the case that we are trying to solve. But one of the important thigs that i noticed is the ```eval``` in ``` python 2 ``` and ```python 3 ``` is  example on that : 
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
