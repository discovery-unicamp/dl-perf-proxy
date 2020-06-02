### Descrição
Rodamos um training job no SageMaker para cada instância e batch size. Dentre os batch sizes temos `[256, 512, 1024, 2048]` e entre as instâncias temos `p2.xlarge, p2.8xlarge, p2.16xlarge, p3.2xlarge, p3.8xlarge, p3.16xlarge`.

## Execução

Para a construção da imagem e sua transferência para um ECR, seguimos o que está descrito no [README principal](https://github.com/lmcad-unicamp/cloud-ML/tree/sagemaker-image#ap%C3%B3s-a-cria%C3%A7%C3%A3o-do-programa). Depois subimos a imgem para um ECR para podemos usá-la no SageMaker, com o bucket que armazena os dados de treinamento e validação sendo usado em um canal de entrada chamado `train`, utilizando os hiperparâmetros:
```json
{
	"batch-size": "256",
	"epochs": "5",
	"num-gpus": "1",
	"file-output": "output.txt"
}
```

### Organização dos logs
```
logs
├── p2 				
│   ├── result-p2-1-1024-e0.txt # result-{identificação do tipo da instância}-{número de gpus}-{batch size}-e0.txt
│   ├── result-p2-1-2048-e0.txt
│   ├── result-p2-1-256-e0.txt
│   ├── result-p2-1-512-e0.txt
│   ├── result-p2-16-1024-e0.txt
│   ├── result-p2-16-2048-e0.txt
│   ├── result-p2-16-256-e0.txt
│   ├── result-p2-16-512-e0.txt
│   ├── result-p2-8-1024-e0.txt
│   ├── result-p2-8-2048-e0.txt
│   ├── result-p2-8-256-e0.txt
│   └── result-p2-8-512-e0.txt
└── p3
    ├── result-p3-2-1024-e0.txt
    ├── result-p3-2-2048-e0.txt
    ├── result-p3-2-256-e0.txt
    ├── result-p3-2-512-e0.txt
    ├── result-p3-4-1024-e0.txt
    ├── result-p3-4-2048-e0.txt
    ├── result-p3-4-256-e0.txt
    ├── result-p3-4-512-e0.txt
    ├── result-p3-8-1024-e0.txt
    ├── result-p3-8-2048-e0.txt
    ├── result-p3-8-256-e0.txt
    └── result-p3-8-512-e0.txt
```
2 directories, 24 files
