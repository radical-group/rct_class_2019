### Requirement

* Python packages
  - zmq (default)
  - pika

* Python 3+

### Execution instruction:

* pypi installation
  `pip install -r requirements.txt`

#### Function Executor CLI (standalone)

`python executor_cli.py --function min --params 1 2`
* The function executor invokes the function `min()` of the `params` (1,2) (iterable)

`python executor_cli.py --function numpy.min --params [1,2]`
* The function executor invokes the function `numpy.min()` of the `params` [1,2] (list)

* Note that a function should be either built-in or callable from an installed module, no alias is allowed e.g. `numpy as np`. 

#### Dispatcher and Worker (multi-processing)

Two separate terminals are necessary.

(Terminal 1)
`python worker.py` # Starts a worker to pull Task message(s)

(Terminal 2)
`python dispatcher.py` # Starts a dispatcher to push Task message(s)

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


### Other Communication Protocol (In Progress)

* gRPC (test run)
  - `python dispatcher.py --yaml grpc.yml` (gRPC client)
  - `python worker.py --yamll grpc.yml` (gRPC server)

* RPyC (test run)
  - `python dispatcher.py --yaml rpyc.yml` (RPyC client)
  - `python worker.py --yamll rpyc.yml` (RPyC server)


