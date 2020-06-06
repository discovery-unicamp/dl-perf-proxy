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
- ``Validation time: T``: Tempo do processo de validação da época atual. O tempo é indicado por T em segundos. Exemplo:
    - ``Validation time: 0.166088104248``
- ``Epoch time: T``: Tempo para processar a época que se concluiu. Exemplo: 
    - ``Epoch time: 20.8873980045s``


('Tempo de inicializacao: ', 0.2424459457397461)

## Outros scripts

# parse-exec-times.py
Extrai os tempos de execução de um arquivo de log e imprime os tempos no formato JSON.
O seguinte texto ilustra o formato do arquivo JSON:
```
{
    "init": 0.2424459457397461,
    "total_training": 61.253731966,
    "epochs": {
        "1": {
            "steps": {
                "1": 8.6593849659,
                "2": 0.249222993851,
                "3": 0.248422861099,
                "4": 0.255298852921,
                "5": 0.246896982193,
                "6": 0.24797296524,
                "7": 0.245851039886,
                "8": 0.252380132675,
                "9": 0.248777866364,
                "10": 0.248451948166,
                "11": 0.249673843384,
                "12": 0.253015041351,
                "13": 0.246588945389,
                "14": 0.247726202011,
                "15": 0.247699975967,
                "16": 0.258562088013,
                "17": 0.247426986694,
                "18": 0.247100114822,
                "19": 0.248167991638,
                "20": 0.252648830414,
                "21": 0.249297857285,
                "22": 0.247051000595,
                "23": 0.247907161713,
                "24": 0.251134157181,
                "25": 0.248499155045,
                "26": 0.246980190277,
                "27": 0.24848985672,
                "28": 0.245877981186,
                "29": 0.252749919891,
                "30": 0.245944023132,
                "31": 0.247025966644,
                "32": 0.247349977493,
                "33": 0.25328707695,
                "34": 0.247216939926,
                "35": 0.248553991318,
                "36": 0.247315883636,
                "37": 0.251832962036,
                "38": 0.248292922974,
                "39": 0.238184928894
            },
            "validation_time": 0.16608810424,
            "epoch_time": 20.8873980045
        },
        "2": {
            "steps": {
                "1": 0.247350931168,
                "2": 0.253271102905,
                "3": 0.248753070831,
                "4": 0.250194072723,
                "5": 0.250216960907,
                "6": 0.24743103981,
                "7": 0.252125024796,
                "8": 0.248482942581,
                "9": 0.25038599968,
                "10": 0.249089002609,
                "11": 0.251664876938,
                "12": 0.247737884521,
                "13": 0.248335838318,
                "14": 0.249619960785,
                "15": 0.247004032135,
                "16": 0.255190134048,
                "17": 0.247982025146,
                "18": 0.252021074295,
                "19": 0.25257897377,
                "20": 0.252198219299,
                "21": 0.246217012405,
                "22": 0.247967004776,
                "23": 0.246859073639,
                "24": 0.252233982086,
                "25": 0.255368947983,
                "26": 0.250209093094,
                "27": 0.247203826904,
                "28": 0.249933958054,
                "29": 0.247875928879,
                "30": 0.249662876129,
                "31": 0.251096010208,
                "32": 0.252562999725,
                "33": 0.247838020325,
                "34": 0.2508289814,
                "35": 0.248946905136,
                "36": 0.25244808197,
                "37": 0.246782064438,
                "38": 0.247802019119,
                "39": 0.237895011902
            },
            "validation_time": 0.017483949661,
            "epoch_time": 9.90889716148
        },
        "3": {
            "steps": {
                "1": 0.246189117432,
                "2": 0.247493982315,
                "3": 0.247646093369,
                "4": 0.252177000046,
                "5": 0.250502109528,
                "6": 0.248851776123,
                "7": 0.249764204025,
                "8": 0.249166965485,
                "9": 0.253164052963,
                "10": 0.246641874313,
                "11": 0.248012781143,
                "12": 0.247318983078,
                "13": 0.251796960831,
                "14": 0.247665166855,
                "15": 0.248161077499,
                "16": 0.248090028763,
                "17": 0.252168178558,
                "18": 0.247175931931,
                "19": 0.248461008072,
                "20": 0.250655889511,
                "21": 0.252609968185,
                "22": 0.251615047455,
                "23": 0.247447967529,
                "24": 0.248338937759,
                "25": 0.248220920563,
                "26": 0.251745939255,
                "27": 0.249652862549,
                "28": 0.246638059616,
                "29": 0.249111890793,
                "30": 0.24750494957,
                "31": 0.252065181732,
                "32": 0.247078180313,
                "33": 0.248404026031,
                "34": 0.249937057495,
                "35": 0.2600440979,
                "36": 0.248913049698,
                "37": 0.250295877457,
                "38": 0.247709035873,
                "39": 0.231247901917
            },
            "validation_time": 0.017466783523,
            "epoch_time": 9.88619399071
        },
        "4": {
            "steps": {
                "1": 0.25116610527,
                "2": 0.247439146042,
                "3": 0.249898195267,
                "4": 0.249379873276,
                "5": 0.251590967178,
                "6": 0.247051954269,
                "7": 0.251597881317,
                "8": 0.249789953232,
                "9": 0.24963593483,
                "10": 0.254836082458,
                "11": 0.249243974686,
                "12": 0.250152826309,
                "13": 0.249098062515,
                "14": 0.250045061111,
                "15": 0.253296852112,
                "16": 0.250256061554,
                "17": 0.249658107758,
                "18": 0.248975992203,
                "19": 0.253412008286,
                "20": 0.249186038971,
                "21": 0.247797012329,
                "22": 0.248466014862,
                "23": 0.253993988037,
                "24": 0.252097129822,
                "25": 0.253328084946,
                "26": 0.250393867493,
                "27": 0.251507043839,
                "28": 0.249796152115,
                "29": 0.249132156372,
                "30": 0.249456882477,
                "31": 0.253103017807,
                "32": 0.247987985611,
                "33": 0.249405860901,
                "34": 0.250365018845,
                "35": 0.25258398056,
                "36": 0.250073194504,
                "37": 0.249767065048,
                "38": 0.249894142151,
                "39": 0.236093997955
            },
            "validation_time": 0.017088174819,
            "epoch_time": 9.92582702637
        },
        "5": {
            "steps": {
                "1": 0.247256994247,
                "2": 0.248094081879,
                "3": 0.251825094223,
                "4": 0.247916936874,
                "5": 0.247797012329,
                "6": 0.248179197311,
                "7": 0.252763986588,
                "8": 0.251887083054,
                "9": 0.248888015747,
                "10": 0.248607158661,
                "11": 0.249061107635,
                "12": 0.256891965866,
                "13": 0.25026512146,
                "14": 0.248971939087,
                "15": 0.250239133835,
                "16": 0.247915029526,
                "17": 0.252108812332,
                "18": 0.248893022537,
                "19": 0.249422073364,
                "20": 0.249918937683,
                "21": 0.253838062286,
                "22": 0.249199151993,
                "23": 0.249488115311,
                "24": 0.249629974365,
                "25": 0.25848197937,
                "26": 0.249066114426,
                "27": 0.249839067459,
                "28": 0.253468036652,
                "29": 0.252055168152,
                "30": 0.252146959305,
                "31": 0.252611875534,
                "32": 0.247555017471,
                "33": 0.248897075653,
                "34": 0.248736858368,
                "35": 0.252958059311,
                "36": 0.24899315834,
                "37": 0.251221179962,
                "38": 0.24971985817,
                "39": 0.235209941864
            },
            "validation_time": 0.017166137695,
            "epoch_time": 9.92402386665
        }
    }
}

```

# extract-exec-times.sh
Lê os arquivos de log do diretório logs e, para cada arquivo, cria um arquivo "execution-times/VMTYPE/BS/EXP.json" com os tempos de execução do experimento EXP com a máquina virtual VMTYPE e batch size = BS.

Para o exemplo acima, após a execução deste script os seguintes arquivos serão criados.
```
execution-times/
├── p2-1
│   ├── 1024
│   │   └── e0.json
│   ├── 2048
│   │   └── e0.json
│   ├── 256
│   │   └── e0.json
│   └── 512
│       └── e0.json
├── p2-16
│   ├── 1024
│   │   └── e0.json
│   ├── 2048
│   │   └── e0.json
│   ├── 256
│   │   └── e0.json
│   └── 512
│       └── e0.json
├── p2-8
│   ├── 1024
│   │   └── e0.json
│   ├── 2048
│   │   └── e0.json
│   ├── 256
│   │   └── e0.json
│   └── 512
│       └── e0.json
├── p3-2
│   ├── 1024
│   │   └── e0.json
│   ├── 2048
│   │   └── e0.json
│   ├── 256
│   │   └── e0.json
│   └── 512
│       └── e0.json
├── p3-4
│   ├── 1024
│   │   └── e0.json
│   ├── 2048
│   │   └── e0.json
│   ├── 256
│   │   └── e0.json
│   └── 512
│       └── e0.json
└── p3-8
    ├── 1024
    │   └── e0.json
    ├── 2048
    │   └── e0.json
    ├── 256
    │   └── e0.json
    └── 512
        └── e0.json
```