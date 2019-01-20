import os
import re
import glob

def path():
    return os.path.abspath(__file__).replace('utils.pyc','').replace('utils.py','')

#values can be int,float,str,boolean, etc
def inject_values(cmd,values,delim='?'):
    execute = cmd
    if values is not None:
        if type(values) is list:
            for v in values:     #can have multiple value positions
                x = cmd.find(delim) #replace one at a time
                if x>0: execute = execute[:x]+v+execute[x+1:]
        else:
            x = cmd.find(delim)  #replace one at a time
            if x>0: execute = execute[:x]+values+execute[x+1:]
    return execute

#command.sh /arg* --out args/output/*/args
def wild_card_components(cmd,dir='/',wild='*'):
    cmd,comp = re.sub(' +',' ',cmd),{}
    if cmd.find(wild)>0:
        comp = cmd.rsplit(' ')
