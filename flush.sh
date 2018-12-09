#!/bin/bash
sync
echo 3 > /prc/sys/vm/drop_caches
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
