#!/bin/bash

source activate tensorflow_p36
num_gpus=$@
batch=256
i=1
while [ $batch -le 2048 ]
do
    while [ $i -le 5 ]
    do
        output="result-$num_gpus-$batch-e$i.out"
        python mnist_cnn.py $batch $num_gpus &> $output
        (( i++ ))
    done
    (( batch *= 2 ))
    i=1
done
mkdir "numgpu-$num_gpus"
mv "result-$num_gpus"* "numgpu-$num_gpus"
aws s3 cp "numgpu-$num_gpus" s3://mnistlogs/"numgpu-$num_gpus" --recursive
python stop-instance.py 
conda deactivate
#sudo shutdown now
