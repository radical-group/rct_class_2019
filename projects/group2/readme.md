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

