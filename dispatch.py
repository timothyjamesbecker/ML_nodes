#!/usr/bin/env python
import os
import sys
import re
import time
import getpass
import argparse
import socket
import threading
import Queue
import subprocess32 as subprocess
import multiprocessing.dummy as mp
import utils

#[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
#local version of get resources, has no restrictions on I/O and time[[[[[[[[[
#best for long-running and I/O heavy work and extensible via screen[[[[[[[[[[
def get_resources(node,disk_patterns=['/','/data'],verbose=False,rounding=2):
    N = {node:{'cpu':0.0,'mem':0.0,'swap':0.0,'disks':{p:0.0 for p in disk_patterns}}}
    N[node]['err'] = {}
    check = 'top -d 0.25 -n 5 | grep "Cpu" | tail -n 1 && '+\
            'top -n 1 | grep "KiB Mem" && top -n 1 | grep "KiB Swap"'
    check += ' && '+' && '.join(['df -h | grep %s'%p for p in disk_patterns])
    check += ' && sensors | grep "Core"'

    #can check for .tid_nid_jid.json log file?
    #tid= YYYMMDD-HHMMSS
    #test -e .dispatch_*_gaia-12-*.json && echo True || echo False

    command = ["ssh %s -t '%s'"%(node,check)]
    R = {'out':'','err':{}}
    try:
        R['out'] = subprocess.check_output(' '.join(command),
                                           stderr=subprocess.STDOUT,
                                           shell=True)
        R['out'] = R['out'].decode('unicode_escape').encode('ascii','ignore')
    except subprocess.CalledProcessError as E:
        R['err']['output']  = E.output
        R['err']['message'] = E.message
        R['err']['code']    = E.returncode
    except OSError as E:
        R['err']['output']  = E.strerror
        R['err']['message'] = E.message
        R['err']['code']    = E.errno
    #parse and convert the resource query
    for line in R['out'].split('\n'):
        line = line.replace('\x1b',' ').replace('(B',' ').replace('[m',' ').replace('[1m',' ').replace('[',' ')
        line = re.sub(' +',' ',line)
        try:
            if line.startswith('%Cpu(s)'):
                cleaned        = float(line.split(',')[3].strip(' ').split(' ')[1])
                idle_cpu       = round(100.0-cleaned,rounding)
                N[node]['cpu'] = idle_cpu
        except Exception as E:
            N[node]['err']['cpu'] = E.message
            pass
        try:
            if line.startswith('KiB Mem'):
                total_mem      = float(line.split(',')[0].strip(' ').split(' ')[4])
                free_mem       = float(line.split(',')[1].strip(' ').split(' ')[1])
                N[node]['mem'] = round(100.0*(1.0-free_mem/total_mem),rounding)
        except Exception as E:
            N[node]['err']['mem'] = E.message
            pass
        try:
            if line.startswith('KiB Swap'):
                total_swap      = float(line.split(',')[0].strip(' ').split(' ')[3])
                free_swap       = float(line.split(',')[1].strip(' ').split(' ')[1])
                N[node]['swap'] = round(100.0-100.0*(free_swap/total_swap),rounding)
        except Exception as E:
            N[node]['err']['swap'] = E.message
            pass
        try:
            if line.startswith('/dev/'):
                disk = line.replace('\r','').replace('\n','')
                for p in disk_patterns:
                    if disk.endswith(p):
                        N[node]['disks'][p] = round(float(disk.split(' ')[-2].replace('%','')),rounding)
        except Exception as E:
            N[node]['err']['disks'] = E.message
            pass
        try:
            if line.startswith('Core'):
                core = line.replace('\r','').replace('\n','')
                core_numb = int(line.split(':')[0].replace(' ','').split('Core')[-1])
                core_temp = float(re.sub(' +',' ',line).split(':')[-1].strip(' ').split(' ')[0].split('C')[0])
                if 'core_temp' not in N[node]:
                    N[node]['core_temp'] = {core_numb:core_temp}
                else:
                    N[node]['core_temp'][core_numb] = core_temp
        except Exception as E:
            N[node]['err'][''] = E.message
            pass
    if N[node]['err'] != {}: N[node]['err']['out'] = R['out']
    else:                    N[node].pop('err')
    if 'core_temp' in N[node]:
        x,ks = 0.0,N[node]['core_temp'].keys()
        for k in ks:
            x += N[node]['core_temp'][k]
            N[node]['core_temp'].pop(k)
        if len(ks)>0: x /= len(ks)
        N[node]['core_temp'] = x
    return {'status':N}

#[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
#local version of command dispatcher[[[[[[[[[[[[[[[[[[[
#best for long running I/O and unrestricted use[[[[[[[[
#cmd is actual a command queue called tasks now...
def command_runner(cx,node,env=None,verbose=False):
    while True:
        task = tasks.get()
        jid,cmd,values = task['jid'],task['cmd'],task['values']
        cmd = inject_values(cmd,values)

        #write to .tid_nid_jid.json log file
        #["ssh -t 'touch .tid_nid_jid.json'"]

        if not args.sudo:
            command = ["ssh %s -t '%s'"%(node,cmd)]
        else:
            command = ["ssh %s -t \"echo '%s' | sudo -S %s\""%(node,cx['pwd'],cmd)]
        R = {node:{'out':'','err':{},'jid':jid}}
        try:
            if env is None:
                R[node]['out'] = subprocess.check_output(' '.join(command),
                                                         stderr=subprocess.STDOUT,
                                                         shell=True)
            else:
                R[node]['out'] = subprocess.check_output(' '.join(command),
                                                         stderr=subprocess.STDOUT,
                                                         shell=True,
                                                         env=env)
            R[node]['out'] = R[node]['out'].decode('unicode_escape').encode('ascii','ignore')
        except subprocess.CalledProcessError as E:
            R[node]['err']['output']  = E.output
            R[node]['err']['message'] = E.message
            R[node]['err']['code']    = E.returncode
        except OSError as E:
            R[node]['err']['output']  = E.strerror
            R[node]['err']['message'] = E.message
            R[node]['err']['code']    = E.errno
        if R[node]['err']=={}: R[node].pop('err')

        #execution is finished so delete the .tid_nid_jid.json log file
        # ["ssh -t 'rm .tid_nid_jid.json'"]

        results.put({'cmd':R})
        if 'sleep' in task: time.sleep(task['sleep']) #cool down or rest node for some time in sec
        tasks.task_done() #this will release the task and get a new one if not empty

def flush_cache(cx,node):
    cmd = utils.path()+'flush.sh'
    command = ["ssh %s -t \"echo '%s' | sudo -S %s\""%(node,cx['pwd'],cmd)]
    R = {node:{'out':'','err':{}}}
    try:
        R[node]['out'] = subprocess.check_output(' '.join(command),
                                                 stderr=subprocess.STDOUT,
                                                 shell=True)
        R[node]['out'] = R[node]['out'].decode('unicode_escape').encode('ascii','ignore')
    except subprocess.CalledProcessError as E:
        R[node]['err']['output']  = E.output
        R[node]['err']['message'] = E.message
        R[node]['err']['code']    = E.returncode
    except OSError as E:
        R[node]['err']['output']  = E.strerror
        R[node]['err']['message'] = E.message
        R[node]['err']['code']    = E.errno
    if R[node]['err'] == {}: R[node].pop('err')
    return {'flush':R}

#values can be int,float,str,boolean, etc
def inject_values(cmd,values,delim='?'):
    execute = cmd
    if values is not None:
        for v in values[i]:     #can have multiple value positions
            x = cmd.find(delim) #replace one at a time
            if x>0: execute = execute[:x]+v+execute[x+1:]
    return execute

des = """
-------------------------------------------------------------------------------
multi-node  ssh/process based multithreaded dispatching client\n11/18/2018-12/30/2018\tTimothy James Becker

(1) use head,port,targets,values to dispatch similiar commands to targets
(2) when values is larger than #hosts, they are queued automatically async
-------------------------------------------------------------------------------"""
parser = argparse.ArgumentParser(description=des,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--head',type=str,help='hostname of headnode\t\t\t[None]')
parser.add_argument('--port',type=int,help='command port\t\t\t\t[22]')
parser.add_argument('--targets',type=str,help='comma seperated list of host targets\t[/etc/hosts file from head]')
parser.add_argument('--threads',type=int,help='change the default number of threads\t[#targets]')
parser.add_argument('--values',type=str,help='comma seperated list of insertion values for ? chars')
parser.add_argument('--command',type=str,help='command to dispatch\t\t\t[ls -lh]')
parser.add_argument('--sleep',type=int,help='sleep interval between task allocation\t[None]')
parser.add_argument('--sudo',action='store_true',help='elevate the remote dispatched commands\t[False]')
parser.add_argument('--check_prior',action='store_true',help='check cpu,mem,swap,disk prior to command\t[False]')
parser.add_argument('--flush',action='store_true',help='flush caches/containers after I|O/jobs\t[False]')
parser.add_argument('--verbose',action='store_true',help='output more results to stdout\t\t[True]')
args = parser.parse_args()

if args.head is not None:
    head = args.head.split('.')[0]
    domain = '.'+'.'.join(args.head.split('.')[1:])
else:
    head = socket.gethostname()
    domain = ''
if args.port is not None:
    port = args.port
else:
    port = 22
if args.targets is not None:
    nodes = sorted(args.targets.split(','))
elif os.path.exists('/etc/hosts'):
    nodes = None
else:
    raise IOError
if args.command is not None:
    cmd = args.command
else:
    cmd = None
# --values v1a:v2a,v2,v3, v1a is first done, then v2a is done
if cmd is not None and args.values is not None:
    V = []
    values = args.values.split(',')
    for v in values:
        V += [v.split(';')] #in case of multiple value insertions
    values = V
else:
    values = None

uid,pwd = False,False
if args.sudo or args.flush:
    print('user:'),
    uid = sys.stdin.readline().replace('\n','')
    pwd = getpass.getpass(prompt='pwd: ',stream=None).replace('\n','')
cx = {'host':head+domain,'port':port,'uid':uid,'pwd':pwd}
if nodes is None:
    #local=====================================================================================
    command = ['cat /etc/hosts']
    H = {'out':'','err':{}}
    try:
        H['out'] = subprocess.check_output(' '.join(command),
                                           stderr=subprocess.STDOUT,
                                           shell=True)
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
    try:
        s = subprocess.check_output(['reset'],shell=True)
    except subprocess.CalledProcessError as E:
        pass
    except OSError as E:
        pass
    #local=====================================================================================
    time.sleep(0.1)
N,R,threads,jobs = {},[],1,1 #jobs are queued when > threads
if args.threads is not None: threads = args.threads
else:                        threads = len(nodes)
if values is not None:       jobs = len(values)
else:                        jobs = threads
print('using %s number of connection threads'%threads)
print('for %s number of compute jobs'%jobs)

#global data structures for synchronization patterns------
result_list = [] #async queue to put results for || stages
results     = Queue.Queue(maxsize=jobs)
tasks       = Queue.Queue(maxsize=jobs)
def collect_results(result):
    result_list.append(result)
#gloabl data structures for synchronization patterns------

if __name__=='__main__':
    start = time.time()

    if args.check_prior: #execute a resource check
        print('checking prior percent used resources on nodes: %s ..'%nodes)
        #dispatch resource checks to all nodes-------------------------------------
        p1 = mp.Pool(threads)
        for node in nodes:
            p1.apply_async(get_resources,
                           args=(node,['/','/data'],(not args.verbose),2),
                           callback=collect_results)
            time.sleep(0.1)
        p1.close()
        p1.join()
        try:
            s = subprocess.check_output(['reset'],shell=True)
        except subprocess.CalledProcessError as E: pass
        except OSError as E:                       pass
        #collect results---------------------------------------------------------
        for l in result_list: R += [l]
        result_list = []

        #look at cpu and top search for python to see if other things are running?
        #look at secret log file that gets generated for each jid....

    if cmd is not None:
        t_start = time.time()

        if args.sleep is not None:
            work=[{'jid':i,'cmd':cmd,'values':values,'sleep':args.sleep} for i in range(jobs)]

        else:
            work = [{'jid':i,'cmd':cmd,'values':values} for i in range(jobs)]

        #[1]master dispatch_tid.json which has {'work':work}

        for i in range(threads):
            print('starting remote control thread for host=%s'%nodes[i])
            t = threading.Thread(target=command_runner,args=(cx,nodes[i]))
            t.daemon = True
            t.start()
        for i in range(jobs):
            print('enqueuing jid %s'%i)
            tasks.put(work[i])
        tasks.join()
        t_stop = time.time()
        try:
            s = subprocess.check_output(['reset'],shell=True)
        except subprocess.CalledProcessError as E: pass
        except OSError as E:                       pass
        while not results.empty(): R += [results.get()]

    if args.flush:
        print('flushing caches to clear free memory...')
        p1 = mp.Pool(threads)
        for node in nodes:
            p1.apply_async(flush_cache,
                           args=(cx,node),
                           callback=collect_results)
            time.sleep(0.1)
        p1.close()
        p1.join()
        for l in result_list: R += [l]
        result_list = []
    if not args.check_prior: #execute a resource check
        print('checking posterior percent used resources on nodes: %s ..'%nodes)
        #dispatch resource checks to all nodes-------------------------------------
        p1 = mp.Pool(threads)
        for node in nodes:
            p1.apply_async(get_resources,
                           args=(node,['/','/data'],(not args.verbose),2),
                           callback=collect_results)
            time.sleep(0.1)
        p1.close()
        p1.join()
        try:
            s = subprocess.check_output(['reset'],shell=True)
        except subprocess.CalledProcessError as E: pass
        except OSError as E:                       pass
        for l in result_list: R += [l]
        result_list = []
    stop = time.time()
    if not args.verbose:#<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        S,padding = {},40
        for r in R: #{'status':{'node':{outputs...}}}
            t = r.keys()[0]
            n = r[t].keys()[0]
            if t in S: S[t][n] = r[t][n]
            else:      S[t]    = {n:r[t][n]}
        for t in sorted(S.keys()): #cmd, flush, status
            print(''.join(['<' for i in range(padding)])+'results for %s'%t+''.join(['>' for i in range(padding)]))
            for n in sorted(S[t].keys()):
                #R = {node:{'out':'','err':{},'jid':jid}}
                if 'out' in S[t][n]:
                    out = re.sub('\n+','\n',re.sub(' +',' ',S[t][n]['out'].replace('\r','')))
                    if out.endswith('\n'): out = out[:-1]
                    print('%s:\n%s'%(''.join([':' for i in range(padding)])+\
                                     n+''.join([':' for i in range(padding)]),out))
                else:
                    print('%s: %s'%(n,S[t][n]))
        print('processing completed in %s sec'%round(stop-start,2))
    #close it down----------------------------------------------------------------------