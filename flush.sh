#!/bin/bash
sync
echo 3 > /proc/sys/vm/drop_caches
swapoff -a
swapon -a
im=$(docker ps -a -q)
if [[ $im ]]; then
	docker stop $im
	docker rm $im
else
	echo "no running docker containers found..."
fi
