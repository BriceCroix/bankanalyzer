# bankanalyzer


## Developer's corner

Configure virtual environment :

- On windows :
```shell
py -m venv venv
.\env\Scripts\activate
pip install -r requirements.txt
```

- On linux :
```shell
sudo apt install libcairo2-dev pkg-config python3-dev
python3 -m venv venv
source env/bin/activate
pip install -r requirements.txt
```

If you need to install new packages, please update and commit the `requirements.txt` as follow :

```shell
pip install my_new_package
pip freeze > requirements.txt
```

You are now ready to execute `bankanalyzer` with :

```shell
python3 bankanalyzer
```

The executable `bankanalyzer` can be compiled to a single executable with [pyinstaller](https://pypi.org/project/pyinstaller/) :

- On linux :
```shell

```

- On windows :
```shell
pyinstaller --clean --onefile --paths venv\Lib\site-packages --paths .\bankanalyzer\ --name "bankanalyzer" .\bankanalyzer\__main__.py
```