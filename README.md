* `Dockerfile` -> contém os programas, SO, e arquivos para serem levados ao contâiner
* `requirement.txt` -> Contém os pacotes para serem instalados
* `run.sh` -> Arquivo que será executado ao iniciar o Docker (deve ser modificado para "train")
* `FCN_utils.py` e `pymei.py` -> Bibliotecas necessárias para a execução da aplicação
* `03_FCN_train_sm.py` -> aplicação principal que deve ser executada

# Criando contâiners para o SageMaker com GPU

## Requisitos 

* [Docker (19.03+)](https://docs.docker.com/install/) </br>
* [nvidia-docker (2.0+)](https://github.com/NVIDIA/nvidia-docker)</br>
* [Driver da NVIDIA](https://github.com/NVIDIA/nvidia-docker/wiki/Frequently-Asked-Questions#how-do-i-install-the-nvidia-driver)</br>
Não é necessária a instalação do cuda no host, mas precisaremos do driver.</br>

## Criando o Dockerfile

```Dockerfile
FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04
```
A imagem usada já vem com o cuda e outras dependências para o uso de GPU.
```Dockerfile
# set the working directory
RUN ["mkdir", "/opt/program/"]
WORKDIR "/opt/program"
```
De acordo com o padrão, o código deve estar em `/opt/program` (primeira referência). </br>
```Dockerfile
RUN apt-get update && apt-get install -y python python-pip
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get install -y --no-install-recommends python-tk git
```
Instalo dependenências necessárias, escapando de interações na hora da instalação como a de escolher a timezone com a flag `DEBIAN_FRONTEND=noninteractive`.
```Dockerfile
COPY "requirements.txt" .

RUN ["pip", "install", "--upgrade", "pip"]
RUN ["pip", "install", "-r", "requirements.txt"]

RUN ["mkdir", "/opt/ml/"]
RUN ["mkdir","/opt/ml/model/"]
RUN ["mkdir","/opt/ml/output/"]
RUN ["mkdir", "/opt/ml/input"]
RUN ["mkdir", "/opt/ml/input/config"]
RUN ["mkdir", "/opt/ml/input/data"]
```
Aqui instalamos as dependências do pip e depois criamos os diretórios definidos por padrão dos contâiners sagemaker: `/opt/ml/model` é o diretório em que os modelos serão salvos após o treinamento e `/opt/ml/output` é onde podemos colocar as mensagens de erro num arquivo chamdo `failure`. Os dados de entrada por canais estrão em `/opt/ml/input/data/NOME_DO_CANAL/`, no caso o nome do canal escolhido foi train, mas essa pasta não precisa ser criada pelo Dockerfile, o SageMaker irá criá-la sozinho e só  no código em python nós temos que colocar esse caminho.
```Dockerfile
ENV PATH="/opt/program:${PATH}"
COPY "train" .
RUN chmod +x train

# install environment dependencies
COPY "app.py" .
COPY "run.sh" .
COPY "03_FCN_trainer_sm.py" .
COPY "FCN_utils.py" .
COPY "utils.py" .
COPY "pymei.py" .
COPY "add_credentials.sh" .
RUN chmod +x add_credentials.sh
RUN ./add_credentials.sh

EXPOSE 8080
```
Adicionamos `/opt/program` ao PATH e damos permissões de executável para train para podermos chamar `docker run {nome_da_imagem} train` sem problemas. Depois adicionamos todos os scripts necessários para o programa no diretório `/opt/program/` e fazemos outras operações relacionadas ao programa.

## Script train

Nesse projeto nosso script train é feito em python, e começa a partir de um template.

### Inicialização
```python
from __future__ import print_function

import os
import json
import sys
import subprocess
import traceback

# These are the paths to where SageMaker mounts interesting things in your container.
prefix = '/opt/ml/'
#input_path = os.path.join(prefix,'input/data')
output_path = os.path.join(prefix, 'output')
model_path = os.path.join(prefix, 'model')
param_path = os.path.join(prefix, 'input/config/hyperparameters.json')
```
Primeiramente importamos os módulos necessários, como se pode perceber nenhum módulo usado para treinamento (como tensorflow, keras) é importando, pois o script train serve para chamar os scripts propriamente ditos. Outra coisa importante é o `from __future__ import print_function`, como estamos usando python2 e queremos usar a print como no python3 usamos essa função, se posteriormente substituirmos python2 por 3, deveremos tirar essa linha. Em relação às variáveis `*_path`, são usadas para encontrarmos os caminhos definidos por padrão do output, do modelo após o treinamento e dos hyperparâmetros (como não estamos usando o `input/data` preferi deixar comentado.

### Funções 
```python
# Execute your training algorithm.
def _run(cmd):
    """Invokes your training algorithm."""
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
    stdout, stderr = process.communicate()

    return_code = process.poll()
    if return_code:
        error_msg = 'Return Code: {}, CMD: {}, Err: {}'.format(return_code, cmd, stderr)
        raise Exception(error_msg)
```
É na função `_run` que o algoritmo de treinamento é chamado, usamos subprocess.Popen para chamar o script de python responsável por ele como se fosse no bash, cmd é um lista que cada elemento é uma parte do comando. 
```python
def _hyperparameters_to_cmd_args(hyperparameters):
    """
    Converts our hyperparameters, in json format, into key-value pair suitable for passing to our training
    algorithm.
    """
    cmd_args_list = []

    for key, value in hyperparameters.items():
        cmd_args_list.append('--{}'.format(key))
        cmd_args_list.append(value)

    return cmd_args_list

```
Nessa função recebemos um dicionário de hyperparâmetros e retornamos uma lista na forma de argumentos de um comando. 

### Main 
```python
        with open(param_path, 'r') as tc:
            training_params = json.load(tc)

        python_executable = sys.executable
        cmd_args = _hyperparameters_to_cmd_args(training_params)

        train_cmd = [python_executable, training_script] + list(map(str,cmd_args))

        _run(train_cmd)
        print('Training complete.')

        # A zero exit code causes the job to be marked a Succeeded.
        sys.exit(0)
```
Nós carregamos o json que os hyperparâmetros estão (é bom lembrar que todos os valores são mandados como string pelo sagemaker, cabe ao desenvolvedor convertê-los), juntamos os argumentos ao comando principal e mandamos para a função `_run`, se tudo correr bem, será printado `Training Complete` e o programa retornará 0.
```python
    except Exception as e:
        # Write out an error file. This will be returned as the failureReason in the
        # DescribeTrainingJob result.
        trc = traceback.format_exc()
        with open(os.path.join(output_path, 'failure'), 'w') as s:
           s.write('Exception during training: ' + str(e) + '\n' + trc)
        # Printing this causes the exception to be in the training job logs, as well.
        print('Exception during training: ' + str(e) + '\n' + trc, file=sys.stderr)
        # A non-zero exit code causes the training job to be marked as Failed.
        sys.exit(255)
```
Caso aconteça algum erro na execução, a mensagem será escrita no arquivo failure e o programa retornará 255.

## Arquivos do programa

Depois do train e do Dockerfile, a única preocupação é a de escrever as saídas nos locais certos (`/opt/ml/model` e `/opt/ml/output`) e receber os argumentos dos hyperparâmetros, para isso, poderá ser utilizada a biblioteca `argparse`

## Após a criação do programa

### Docker build 

Damos o build como se fosse um container normal, mas com a tag seguindo o padrão `{id do usuário no aws}.dkr.ecr.{região}.amazonaws.com/{nome do repositório}`
Exemplo: `docker build . --rm -t 443768467847.dkr.ecr.us-east-2.amazonaws.com/fcn-trainer-sm`

### Docker run

Para rodar seu container, usamos o `docker run` com a flag `--gpus all`. Exemplo `docker run --gpus all 443768467847.dkr.ecr.us-east-2.amazonaws.com/fcn-trainer-sm train`

### Docker push

Para enviar seu container para o repositório ECR: `docker push {id do usuário no aws}.dkr.ecr.{região}.amazonaws.com/{nome do repositório}`. </br>
OBS: Certifique-se que antes você logou pelo `docker login  {id do usuário no aws}.dkr.ecr.{região}.amazonaws.com/`

## Referências 
1. Overview of containers for Amazon SageMaker: https://sagemaker-workshop.com/custom/containers.html

2. Building your own algorithm container: https://github.com/awslabs/amazon-sagemaker-examples/blob/master/advanced_functionality/scikit_bring_your_own/scikit_bring_your_own.ipynb
3. Pushing an Image: https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.htm
