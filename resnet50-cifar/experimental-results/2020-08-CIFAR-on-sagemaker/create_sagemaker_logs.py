from utils import *
import json
import argparse
import boto3

parser = argparse.ArgumentParser()

parser.add_argument("filename", help="path of yaml file", type=str)

args = parser.parse_args()

yaml_filepath = args.filename

client = boto3.client("sagemaker")


with open(yaml_filepath, 'r') as yaml_file:
    for tj_name in (yaml_to_tj_names(yaml_file.read())):
        describe = client.describe_training_job(TrainingJobName = tj_name)
        with open(f"./sagemaker-logs/{tj_name}.json","w") as json_file:
            json_file.write(json.dumps(describe, default=datetime_json_converter, indent=4))
        with open(f"./sagemaker-logs/{tj_name}.summary","w") as summary_file:
            print(f"{tj_name} saved in sagemaker-logs: \n\t- sagemaker-logs/{tj_name}.json\n\t- sagemaker-logs/{tj_name}.summary")
            name = describe["TrainingJobName"] 
            instance = describe["ResourceConfig"]["InstanceType"]
            summary_file.write(f"name: {name}\n")
            summary_file.write(f"instance: {instance}\n")
            summary_file.write("hyperparameters:\n")
            for hyperparameter in describe["HyperParameters"]:
                summary_file.write(f"\t{hyperparameter}: {describe['HyperParameters'][hyperparameter]}\n")
            billable_time = describe["BillableTimeInSeconds"]
            total_training_time = describe["TrainingTimeInSeconds"]
            summary_file.write(f"billable time: {billable_time}\n")
            summary_file.write(f"total training time: {total_training_time}\n") 
            summary_file.write("transitions:\n")
            for secondary_transition in describe['SecondaryStatusTransitions']:
                status = secondary_transition["Status"]
                time_secondary = (secondary_transition["EndTime"] -  secondary_transition["StartTime"]).total_seconds()
                summary_file.write(f"\tstatus [{status}] - duration: {time_secondary}\n")
