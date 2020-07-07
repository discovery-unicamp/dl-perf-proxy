# Experimental Setup
 
Arquivo descrevendo o setup de cada experimento realizado e salvo nesse diretório.

Para cada experimento a informação será mostrada da forma 
```
<Tipo da instância>-<Número de Gpus>-<Batch Size>-<Experimento>: 
	* <Informação>
	...
```
## Ambiente

Fizemos os experimentos `e0` no Amazon SageMaker, a partir de TrainingJobs.

## Imagens usadas no Treinamento

* `p2-1-*-e0`: 
	* Imagem base: `nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04` 
	* Imagem final (Repositório ECR): `245983579475.dkr.ecr.us-east-1.amazonaws.com/mnist-sagemaker@sha256:2d3758d3a86e1d5c034d8a6918189355ee6865d43429fb3202e989721e31ef8a`
	* Python: `3.6`
	* Tensorflow: `tensorflow-gpu==1.14`
	* Keras: `2.3.1` 
	* CUDA: `10.0.130`
	* CudNN: `7.6.5.32`

* `p2-8-*-e0`:
	* Imagem base: `tensorflow/tensorflow:1.14.0-gpu-py3` 
	* Imagem final (Repositório ECR): `245983579475.dkr.ecr.us-east-1.amazonaws.com/mnist-sagemaker@sha256:219127459f82d60e1e447ab78ed5fabd80a6d15abf08bfc5b922d6eb017db318` (latest)
	* Python: `3.6`
	* Tensorflow: `tensorflow-gpu==1.14`
	* Keras: `2.3.1` 
	* CUDA: `10.0.130`
	* CudNN: `7.4.1.5-1`

* `p2-16-*-e0`:
	* Imagem base: `tensorflow/tensorflow:1.14.0-gpu-py3` 
	* Imagem final (Repositório ECR): `245983579475.dkr.ecr.us-east-1.amazonaws.com/mnist-sagemaker@sha256:219127459f82d60e1e447ab78ed5fabd80a6d15abf08bfc5b922d6eb017db318` (latest)
	* Python: `3.6`
	* Tensorflow: `tensorflow-gpu==1.14`
	* Keras: `2.3.1` 
	* CUDA: `10.0.130`
	* CudNN: `7.4.1.5-1`

* `p3-*-*-e0`:
	* Imagem base: `tensorflow/tensorflow:1.14.0-gpu-py3` 
	* Imagem final (Repositório ECR): `245983579475.dkr.ecr.us-east-1.amazonaws.com/mnist-sagemaker@sha256:219127459f82d60e1e447ab78ed5fabd80a6d15abf08bfc5b922d6eb017db318` (latest)
	* Python: `3.6`
	* Tensorflow: `tensorflow-gpu==1.14`
	* Keras: `2.3.1` 
	* CUDA: `10.0.130`
	* CudNN: `7.4.1.5-1`

## Hiperparâmetros utilizados 

* `num-gpus`: Números de GPUS máximos suportados por cada instância
* `batch-size`: Batch size utilizado no experimento 
* `epochs`: 5 
