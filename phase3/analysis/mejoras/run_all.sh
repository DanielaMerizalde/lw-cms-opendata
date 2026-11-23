#!/bin/bash
# host: runs v3 on all signal blocks, 8 in parallel
cd "$(dirname "$0")"
cat lists/all.txt | xargs -P 8 -L 1 bash -c 'docker exec lw3b-sig bash /work/mejoras/run_v3.sh /work/mejoras/lists/$1.txt /work/mejoras/out/$0/$1.root > logs/$1.log 2>&1 && echo "OK $1" || echo "FAIL $1"'
