#!/usr/bin/env python
import os
import math
import random
import time
import sys
import glob
import argparse
import multiprocessing as mp

#cpu load with mult,add,random,pow,trig,store
def run_load(s):
    start,x = time.time(),1
    while True:
        curr = time.time()
        if curr-start > s:
            break
        else:
            x = min(int(1E9),max(1,x+math.cos(x)+random.randint(-10,10)*x))
    return x

#puts data back together
result_list = [] #async queue to put results for || stages
def collect_results(result):
    result_list.append(result)

des = """distributed compute path, time, testing utilities"""
parser = argparse.ArgumentParser(description=des,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-s','--secs',type=int,help='seconds of processing\t[1]')
parser.add_argument('-l','--load',type=int,help='cpu core(s) to load\t[1]')
args = parser.parse_args()
if args.secs is not None: secs = args.secs
else:                     secs = 1
if args.load is not None: load = args.load
else:                     load = 1

if __name__=='__main__':
    t_start = time.time()

    p1 = mp.Pool(load)
    for l in range(load):  # each site in ||
        p1.apply_async(run_load,
                       args=(secs,),
                       callback=collect_results)
        time.sleep(0.1)
    p1.close()
    p1.join()

    R = []
    for l in result_list: R += [l]

    t_stop = time.time()
    print('%s cpus were loaded for %s secs\n output: %s'%(load,round(t_stop-t_start,2),R))