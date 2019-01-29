Instructions

1. Install conda

2. Get packages
```sh
conda env create -f environment.yml
source activate rp
```

3. Open up 3 terminals

Terminal 1:
```sh
python queue.py
```

Terminal 2:
```sh
python client.py
```

Terminal 3:
```sh
python executor.py
```