#!/bin/bash

source activate tensorflow_cpu
num_gpus=$@
batch=256
i=1
while [ $batch -le 2048 ]
do
    while [ $i -le 5 ]
    do
        output="result-$num_gpus-$batch-e$i.out"
        python 03_FCN_trainer.py $batch $num_gpus &> $output
        (( i++ ))
    done
    (( batch *= 2 ))
    i=1
done 
conda deactivate
#sudo shutdown now
