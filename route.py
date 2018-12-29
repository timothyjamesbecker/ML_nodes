#multi-threaded (producer-consumer) workflow tester

import os
import sys
import copy
import time
import datetime
import random
import argparse
import threading
import Queue
import subprocess32 as subprocess
import numpy as np

#init---------------------------------------------------------------------------------------------
des = """producer consumer pattern where producers can be more or less than consumer"""
parser = argparse.ArgumentParser(description=des,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-h','--head',type=str,help='hostname of the head node\t[None]')
parser.add_argument('-t','--threads',type=int,help='number of threads for hosts\t[#hosts]')
parser.add_argument('-j','--jobs',type=int,help='number of jobs to be queued\t[#hosts x2]')
args = parser.parse_args()
#set number of threads to hosts:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if args.head is not None: head = args.head
else:                     raise AttributeError

print('looking for hosts...')
command = ['cat /etc/hosts']
H = {'out':'','err':{}}
try:
    H['out'] = subprocess.check_output(' '.join(command),stderr=subprocess.STDOUT,shell=True)
except subprocess.CalledProcessError as E:
    H['err']['output']   = E.output
    H['err']['message']  = E.message
    H['err']['code']     = E.returncode
except OSError as E:
    H['err']['output']   = E.strerror
    H['err']['message']  = E.message
    H['err']['code']     = E.errno
nodes = []
for line in H['out'].split('\n'):
    if line.find('::') < 0 and not line.startswith('#') and line != '\n' and line != '':
        node = line.split(' ')[-1].split('\t')[-1].replace('\n','')
        if node != head: nodes += [node]
nodes = sorted(nodes)
#could ping the hosts to see if they are there first?
try:
    s = subprocess.check_output(['reset'],shell=True)
except subprocess.CalledProcessError as E:
    pass
except OSError as E:
    pass

if args.threads is not None: threads = args.threads
else:                        threads = len(nodes)
if args.jobs is not None:    jobs = args.jobs
else:                        jobs = threads*2
#set threads to number of hosts:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

compute_nodes = [{'%s'%i:[0,0]} for i in nodes]  #nodeid:[number of successes, number of failures]
work          = [{'cmd':'/media/nfs/data/software/ML_nodes/load.py -s 10 -l 4','values':[]} for i in range(jobs)]
tasks         = Queue.Queue(maxsize=jobs)
#init---------------------------------------------------------------------------------------------

#These are worker threads....
def worker(host):
    while True:
        node       = host.keys()[0]
        status     = host[node]
        task       = tasks.get()
        cmd,values = task['cmd'],task['values']
        command = ["ssh %s -t '%s'"%(node,cmd)]
        out = ''
        try:
            out = subprocess.check_output(' '.join(command),
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        except subprocess.CalledProcessError as E:
            out = E.message
            pass
        except OSError as E:
            out = E.message
        print('node=%s out:%s'%(node,out))
        tasks.task_done()

if __name__=='__main__':
    #keep dispatching if you fail, at least one success to continue    
    t_start = time.time()
    #start up a thread for each reachable node.....................
    for i in range(threads):
        t = threading.Thread(target=worker,args=(compute_nodes[i],))
        t.daemon = True
        t.start()
    #because they want work, they are blocking on task.get() line 75
    for i in range(threads): tasks.put(work[i])
    #all blocked threads will grab up some work: load is multi-proccess 100% loading
    tasks.join()
    #block until all work is finished......................................................................
    t_stop = time.time()
    print("\nCompleted all jobs and returned to single execution in %s seconds"%round(t_stop-t_start,1))