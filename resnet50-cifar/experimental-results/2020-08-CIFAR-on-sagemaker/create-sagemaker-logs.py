from utils import *
import json
import argparse
import boto3

parser = argparse.ArgumentParser()

parser.add_argument("filename", help="path of yaml file", type=str)

args = parser.parse_args()

yaml_filepath = args.filename

client = boto3.client("sagemaker")

initial_costs = {
    "ml.p2.xlarge": 0.9,
    "ml.p2.8xlarge": 7.2,
    "ml.p2.16xlarge": 14.4,
    "ml.p3.2xlarge": 3.06,
    "ml.p3.8xlarge": 12.24,
    "ml.p3.16xlarge": 24.48,
    "ml.g4dn.xlarge": 0.526,
    "ml.g4dn.2xlarge": 0.752,
    "ml.g4dn.4xlarge": 1.204,
    "ml.g4dn.8xlarge": 2.176,
    "ml.g4dn.16xlarge": 4.352,
    "ml.g4dn.12xlarge": 3.912
}


with open(yaml_filepath, 'r') as yaml_file:
    for tj_name in (yaml_to_tj_names(yaml_file.read())):
        describe = client.describe_training_job(TrainingJobName = tj_name)
        with open(f"./sagemaker-logs/{tj_name.replace('-real','')}.json","w") as json_file:
            json_file.write(json.dumps(describe, default=datetime_json_converter, indent=4))
        with open(f"./sagemaker-logs/{tj_name.replace('-real','')}.summary","w") as summary_file:
            print(f"{tj_name} saved in sagemaker-logs: \n\t- sagemaker-logs/{tj_name.replace('-real','')}.json\n\t- sagemaker-logs/{tj_name.replace('-real','')}.summary")
            name = describe["TrainingJobName"] 
            instance = describe["ResourceConfig"]["InstanceType"]
            summary_file.write(f"name: {name}\n")
            summary_file.write(f"instance: {instance}\n")
            summary_file.write("hyperparameters:\n")
            for hyperparameter in describe["HyperParameters"]:
                summary_file.write(f"\t{hyperparameter}: {describe['HyperParameters'][hyperparameter]}\n")
            billable_time = describe["BillableTimeInSeconds"]
            cost = initial_costs[instance]/3600 * billable_time
            total_training_time = describe["TrainingTimeInSeconds"]
            summary_file.write(f"billable time: {billable_time}\n")
            summary_file.write(f"cost: U$ {cost:.4f}\n")
            summary_file.write(f"total training time: {total_training_time}\n") 
            summary_file.write("transitions:\n")
            for secondary_transition in describe['SecondaryStatusTransitions']:
                status = secondary_transition["Status"]
                time_secondary = (secondary_transition["EndTime"] -  secondary_transition["StartTime"]).total_seconds()
                summary_file.write(f"\tstatus [{status}] - duration: {time_secondary}\n")
