import os

def path():
    return os.path.abspath(__file__).replace('utils.pyc','').replace('utils.py','')
