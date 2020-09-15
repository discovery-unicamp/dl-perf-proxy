import yaml
from datetime import datetime
import re
def format_name_sagemaker(name,instance, gpu, batch, number, error=False):
    if not error:
        return f"{name}-{instance}-gpu{gpu}-b{batch}-e{number}"
    else:
        return f"{name}-{instance}-gpu{gpu}-b{batch}-e{number}-real"

def format_name_logs(name, instance, gpu, batch, number, error=False):
    return f"result-{instance}-{gpu}-{batch}-e{number}"

def tj_name_to_tuple(tj_name):
    tj_name = tj_name.replace("-real", "")
    pattern = re.compile(r"([\w\d]+)-([\w\d]+)-gpu(\d+)-b([\d]+)-e([\d]+)")
    if pattern.match(tj_name) != None:
        groups = pattern.match(tj_name).groups()
    else:
        print(tj_name)
        return []
    return list(groups)

def yaml_to_tj_names(document):
    """
    reads yaml and return training jobs names according to the training job name pattern used
    """

    yaml_read = yaml.safe_load(document)
    for experiment in yaml_read:
        name = yaml_read[experiment]["name"]
        number = yaml_read[experiment]["number"]
        training_jobs_names = []
        for instance in yaml_read[experiment]["instances"]:
            gpus = str(yaml_read[experiment]["instances"][instance]["gpus"])
            batchs = str(yaml_read[experiment]["instances"][instance]["batchs"])
            if batchs.replace(" ", "") == "all":
                batchs = "256, 512, 1024, 2048"
            
            batchs = batchs.replace(" ","") .split(",")
            for gpu in gpus.replace(" ","").split(","):
                for batch in batchs:
                    training_jobs_names.append(format_name_sagemaker(name, instance, gpu, batch, number))
            if "errors" in yaml_read[experiment]["instances"][instance]:
                for error in str(yaml_read[experiment]["instances"][instance]["errors"]).replace(" ","").split(";"):
                    gpu, batch = error.split(",")
                    training_jobs_names.remove(format_name_sagemaker(name, instance, gpu, batch, number))
                    training_jobs_names.append(format_name_sagemaker(name, instance, gpu, batch, number, True))

    return training_jobs_names

def datetime_json_converter(inp):
    """ 
    Convert datetime to string in json dumps
    """
    if isinstance(inp, datetime):
        return inp.__str__()

if __name__ == "__main__":
    with open("e0-low-cost-instances.yaml",'r') as document:
        for i in yaml_to_tj_names(document):
            print(tj_name_to_tuple(i))
