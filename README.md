# ML_nodes
configuring Ubuntu 16LTS ML nodes

### (2) require.sh
a single command that can configure an Ubuntu 16LTS system for machine learning with the stand alone dispatchpy tool or via the SPARK 2.3.1 framework. SPARK configuration is intentially left out due to the extensive documentation and customization inherient with clusters.

```bash
./require.sh
```

### (1) dispatch.py
##### depends on: python 2.7.12+, parimiko, subprocess32
A general purpose ssh based dispatch tool for running commands across several connected nodes. Can be used remotely using the parimiko module which has acceptable perfromance for squick commands like 'ls'. For more intensive commands like copying large files, removing large files, or running multi-day long commands this module should be run from the head host that is in turn connected to the worker nodes. Remote commands can still be issued to monitor resources using the in built '--check_resources' option which by default will pull all targets and try to obtain the use cpu%, mem%, swap% and each disk mount such as '/'% and '/data'%.  
#####A typical node resource command would be:
```bash
./dispatch.py --head host.domain.com --remote --check_resources --verbose
```
while ssh into the head node before execution  yeilds simplified operation where the local /etc/hosts file is used:
```bash
./dispatch.py --check_resources --verbose
```
#####perform some command across all targets using sudo power:
```bash
./dispatch --targets node1,node2,node3 \ 
--command 'apt update && apt upgrade -y' \ 
--sudo

```
This example will update the ubuntu 16 LTS using the apt tool for all nodes.  Finally to run very intensive and long running work, first check that resources are avaible and then issue the command:
```python
./dispatch.py --check_resources --verbose

screen -L ./dispatch.py --targets node4,node5,node6 \ 
--command '~/long_job.sh -p 1'

```
