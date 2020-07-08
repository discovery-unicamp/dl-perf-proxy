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
aws_access_key_id = AKIAWOUVJOGDVDQNIA7A
aws_secret_access_key = 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
region = us-east-1
EOF
