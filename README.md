# ML_nodes
configuring Ubuntu 16LTS ML nodes

### (2) require.sh
a single command that can configure an Ubuntu 16LTS system for machine learning with the stand alone dispatchpy tool or via the SPARK 2.3.1 framework. SPARK configuration is intentially left out due to the extensive documentation and customization inherient with clusters.

```bash
./require.sh
```

### (1) dispatch.py
##### depends on: python 2.7.12+, subprocess32
A general purpose ssh based dispatch tool for running commands across several connected nodes. For intensive commands like copying large files, removing large files, or running multi-day long commands this module should be run from the head host that is in turn connected to the worker nodes. Remote monitoring of resources uses the system top/sensors internally which will pull all targets and obtain the use cpu-temp in degrees C, cpu%, mem%, swap% and each disk mount such as '/'% and '/data'%.  
#####typical all-cluster resource check would be:
```bash
./dispatch.py
```
which returns an output showing the status if you had eight nodes in addition to the head node:
```python
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<results for status>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
node1: {'mem': 64.33, 'disks': {'/data': 13.0, '/': 10.0}, 'swap': 6.57, 'core_temp': 46.5, 'cpu': 0.0}
node2: {'mem': 64.63, 'disks': {'/data': 13.0, '/': 11.0}, 'swap': 6.19, 'core_temp': 46.5, 'cpu': 0.0}
node3: {'mem': 65.63, 'disks': {'/data': 13.0, '/': 10.0}, 'swap': 2.61, 'core_temp': 45.5, 'cpu': 0.5}
node4: {'mem': 66.11, 'disks': {'/data': 13.0, '/': 11.0}, 'swap': 2.62, 'core_temp': 46.75, 'cpu': 1.0}
node5: {'mem': 66.12, 'disks': {'/data': 13.0, '/': 11.0}, 'swap': 2.55, 'core_temp': 47.0, 'cpu': 0.0}
node6: {'mem': 64.33, 'disks': {'/data': 13.0, '/': 10.0}, 'swap': 2.69, 'core_temp': 45.5, 'cpu': 0.0}
node7: {'mem': 64.74, 'disks': {'/data': 13.0, '/': 11.0}, 'swap': 2.88, 'core_temp': 46.75, 'cpu': 0.0}
node8: {'mem': 65.69, 'disks': {'/data': 13.0, '/': 10.0}, 'swap': 2.56, 'core_temp': 46.25, 'cpu': 0.0}
processing completed in 5.7 sec
```
mem, disks, swap and cpu are % utilized, while core_temp is degrees celsius

#####execute the same command on node1,node2,node3 targets using sudo:
```bash
./dispatch --targets node1,node2,node3 \ 
--command 'apt upgrade -y' \ 
--sudo

```

#### execute different commands in an asynchronous queue using value injection
```bash
./dispatch --targets node1,node2 \
--command 'job -p 1 -i /data/?.txt -o /data/?.dat'
--values 'file1;result1,file2;result2,file3;result3,file4;result4'

```
This last example will run one command at a time on node1 and node2 while the third and forth jobs will wait for the first job to finish before starting execution.

### (2) load.py
##### depends on: python 2.7.12+
Allows for load testing in terms of -l cpu cores to load at 100% and -s seconds to execute that loading.
```bash
./load.py -s 20 -l 4
```
In the example we use 4 cores at 100% for 20 seconds time.