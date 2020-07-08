#!/bin/bash

mkdir ~/.aws
#cd ~/.aws
cat <<EOF >~/.aws/config
[default]
region = us-east-1
output = json
EOF
cat <<EOF >~/.aws/credentials
[default]
aws_access_key_id = AKIAWOUVJOGDZT2TZJZC
aws_secret_access_key = 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
EOF


if [[ "$1" = train ]]
then
    python ./03_FCN_trainer_sm.py 256 1 arquivo.txt
    #jupyter nbconvert --execute --ExecutePreprocessor.timeout=-1 --to notebook --inplace 03_FCN_trainer_sm.py 256 1 arquivo.txt
else
    python -c "import t4; t4.Package.install('quilt/quilt_sagemaker_demo', registry='s3://quilt-example', dest='.')"
    cp quilt/quilt_sagemaker_demo/clf.h5 clf.h5
    rm -rf quilt/
    python -m flask run --host=0.0.0.0 --port=8080
fi

