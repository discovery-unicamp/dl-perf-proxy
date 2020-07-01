### Descrição
Rodamos um training job no SageMaker para cada instância e batch size. Dentre os batch sizes temos `[256, 512, 1024, 2048]` e entre as instâncias temos `p2.xlarge, p2.8xlarge, p2.16xlarge, p3.2xlarge, p3.8xlarge, p3.16xlarge`.

## Execução

Inicialmente, construimos a imagem da VM seguindo os passos descritos no [README principal](https://github.com/lmcad-unicamp/cloud-ML/tree/sagemaker-image#ap%C3%B3s-a-cria%C3%A7%C3%A3o-do-programa).
Depois subimos a imagem para um ECR para usá-la no SageMaker, com o bucket que armazena os dados de treinamento e validação sendo usado em um canal de entrada chamado `train`, utilizando os hiperparâmetros:
```json
{
	"batch-size": "256",
	"epochs": "5",
	"num-gpus": "1",
	"file-output": "output.txt"
}
```


### Organização dos logs

Para cada par <BS,VMTYPE>, onde BS indica o tamanho do batch e VMTYPE o tipo da máquina virtual, executamos um experimento usando uma instância do tipo VMTYPE e com batch size = BS.
O log de execução de cada execução está gravado no diretório logs utilizando um nome com a seguinte convenção:
``result-VMTYPE-BS-eN.txt``
Onde ``VMTYPE`` indica o tipo da máquina virtual (p2-1, p2-16, ... para p2.xlarge, p2.16xlarge, ...), ``BS`` indica o tamanho do batch durante o treinamento e ``N`` indica o número do experimento (serve para diferenciar múltiplas execuções do mesmo experimento).

```
logs
├── result-p2-1-1024-e0.txt
├── result-p2-1-2048-e0.txt
├── result-p2-1-256-e0.txt
├── result-p2-1-512-e0.txt
├── result-p2-16-1024-e0.txt
├── result-p2-16-2048-e0.txt
├── result-p2-16-256-e0.txt
├── result-p2-16-512-e0.txt
├── result-p2-8-1024-e0.txt
├── result-p2-8-2048-e0.txt
├── result-p2-8-256-e0.txt
├── result-p2-8-512-e0.txt
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

### Formato dos logs

Cada log contém todo o texto impresso no terminal pelo programa durante sua execução. 
Os seguintes trechos indicam os tempos de execução medidos durante a execução do programa:

- ``('Tempo de inicializacao: ', T)``: Tempo de inicialização, onde ``T`` indica o tempo em segundos da inicialização do programa até XXXXXX. Exemplo:
    - ``('Tempo de inicializacao: ', 0.2424459457397461)``
- ``Real time: WCT``: onde ``WCT`` indica o wallclock time da máquina em segundos??
    - Esta marcação aparece em diversas posições do log.
- ``I step training time: T``: Tempo de um passo (step) do treinamento, onde I é o índice do passo dentro da época e T é o tempo do passo. Exemplo:
    - ``37 step training time: 0.251832962036s``
- ``I steps training: Ts``: Tempo do último passo (step) de cada época, onde I é o índice do passo dentro da época e T é o tempo do passo. Exemplo:
    - ``40 steps training: 2.58118700981s``
- ``Validation time: T``: Tempo do processo de validação da época atual. O tempo é indicado por T em segundos. Exemplo:
    - ``Validation time: 0.166088104248``
- ``Epoch time: T``: Tempo para processar a época que se concluiu. Exemplo: 
    - ``Epoch time: 20.8873980045s``



## Outros scripts

# parse-exec-times.py
Extrai os tempos de execução de um arquivo de log e imprime os tempos no formato JSON.

# training-times-summary.py
Lê os arquivos JSON produzidos pelo script parse-exec-times.py e produz um resumo das estatísticas dos tempos.

# extract-exec-times.sh
Percorre os arquivos de log do diretório logs e, para cada arquivo:
- cria um arquivo "execution-times/VMTYPE/BS/EXP.json" com os tempos de execução do experimento EXP com a máquina virtual VMTYPE e batch size = BS.
- cria um arquivo "execution-times/VMTYPE/BS/EXP.summary" com o resumo das estatísticas dos tempos.

Para o exemplo acima, após a execução deste script os seguintes arquivos serão criados.
```
execution-times/
├── p2-1
│   ├── 1024
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 2048
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 256
│   │   ├── e0.json
│   │   └── e0.summary
│   └── 512
│       ├── e0.json
│       └── e0.summary
├── p2-16
│   ├── 1024
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 2048
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 256
│   │   ├── e0.json
│   │   └── e0.summary
│   └── 512
│       ├── e0.json
│       └── e0.summary
├── p2-8
│   ├── 1024
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 2048
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 256
│   │   ├── e0.json
│   │   └── e0.summary
│   └── 512
│       ├── e0.json
│       └── e0.summary
├── p3-2
│   ├── 1024
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 2048
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 256
│   │   ├── e0.json
│   │   └── e0.summary
│   └── 512
│       ├── e0.json
│       └── e0.summary
├── p3-4
│   ├── 1024
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 2048
│   │   ├── e0.json
│   │   └── e0.summary
│   ├── 256
│   │   ├── e0.json
│   │   └── e0.summary
│   └── 512
│       ├── e0.json
│       └── e0.summary
└── p3-8
    ├── 1024
    │   ├── e0.json
    │   └── e0.summary
    ├── 2048
    │   ├── e0.json
    │   └── e0.summary
    ├── 256
    │   ├── e0.json
    │   └── e0.summary
    └── 512
        ├── e0.json
        └── e0.summary
```



# plot-step_times_per_epoch.py
Este script lê da entrada padrão um arquivo no formato JSON produzido pelo script ``parse-exec-times.py`` e gera um gráfico com os tempos de execução. O formato do arquivo de saída é definido pelo sufixo do nome do arquivo.

A opção -t pode ser usada para ajusatar o título do gráfico.

# plot-charts.sh
Este script percorre os arquivos json armazenados em ``execution-times/*/*/*.json`` e, para cada arquivo, chama scripts para gerar gráficos.
