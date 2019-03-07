### Execution instruction:

`python executor.py --function min --params "1,2"`
* The function executor executes the function `min` of the `params` (1,2)


### Implementation details:

* Define a set of functions, along with params and resources (cores) in `dispatcher.py` 

```python
task = { 
            'function' : "example_compute.compute_flops",
            'params': [1, 2048],
            'resources': 1
            
            }
```

* Note: `dispatcher.py` can be executed with either `zmq` or `rabbitmq`.

* `dispatcher.py` will sort the messages (tasks) based on priority, i.e., 
based on increasing order of resource requirements and send the messages 
to `worker.py` 

### Implementation Notes: 

* `set_argument()` takes the user input (function and parameters) and parses 
the string, along with the `__import__` modules to the `function_executor()` 

* `worker.py` pulls the messages in the order in which the tasks were received, 
executes the command defined by the task, and sends the output back to client


