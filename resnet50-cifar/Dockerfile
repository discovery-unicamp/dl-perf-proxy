FROM tensorflow/tensorflow:2.0.0-gpu-py3
#RUN apt-get update && apt-get install -y python3.6 python3-pip

# set the working directory
RUN ["mkdir", "/opt/program/"]
WORKDIR "/opt/program"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get install -y --no-install-recommends python-tk 

# install code dependencies
#COPY "requirements.txt" .

#RUN ["pip3", "install", "--upgrade", "pip"]
#RUN ["pip3", "install", "-r", "requirements.txt"]

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
# ADD pic .
# install environment dependencies
#COPY "hyperparameters.json" "/opt/ml/input/config/"

COPY "custom_callback.py" .
COPY "cifar.py" .
