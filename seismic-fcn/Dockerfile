FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04
RUN apt-get update && apt-get install -y python python-pip

# set the working directory
RUN ["mkdir", "/opt/program/"]
WORKDIR "/opt/program"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get install -y --no-install-recommends python-tk git

# install code dependencies
COPY "requirements.txt" .

RUN ["pip", "install", "--upgrade", "pip"]
RUN ["pip", "install", "-r", "requirements.txt"]

RUN ["mkdir", "/opt/ml/"]
RUN ["mkdir","/opt/ml/model/"]
RUN ["mkdir","/opt/ml/output/"]
RUN ["mkdir", "/opt/ml/input"]
RUN ["mkdir", "/opt/ml/input/config"]
RUN ["mkdir", "/opt/ml/input/data"]
RUN ["mkdir", "/opt/ml/input/data/train"]


ENV PATH="/opt/program:${PATH}"
COPY "train" .
RUN chmod +x train
#ADD pic .
# install environment dependencies
#ADD "fcn/" "/opt/ml/input/data/train"
#COPY "hyperparameters.json" "/opt/ml/input/config/"

COPY "custom_callback.py" .
COPY "app.py" .
COPY "run.sh" .
COPY "03_FCN_trainer_sm.py" .
COPY "FCN_utils.py" .
COPY "utils.py" .
COPY "pymei.py" .
COPY "add_credentials.sh" .
RUN chmod +x add_credentials.sh
RUN ./add_credentials.sh
