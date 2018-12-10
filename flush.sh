#!/bin/bash
sync
echo 3 > /proc/sys/vm/drop_caches
im=$(docker ps -a -q)
if [[ $im ]]; then
	docker stop $im
	docker rm $im
else
	echo "no running docker containers found..."
fi
