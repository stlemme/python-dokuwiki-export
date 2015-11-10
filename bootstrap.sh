#!/usr/bin/env bash

MYDIR=$(dirname $0)

./preprocessing.sh

cd $MYDIR && python3 run-jobs.py $FIDOC_JOBS

./postprocessing.sh


