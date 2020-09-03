from utils import *
import argparse
import boto3
import tarfile
import os


parser = argparse.ArgumentParser()

parser.add_argument("filename", help="path of yaml file", type=str)

args = parser.parse_args()

yaml_filepath = args.filename

client = boto3.client("s3")

with open(yaml_filepath,'r') as yaml_file:
    yaml_doc = yaml_file.read()
    for tj_name in yaml_to_tj_names(yaml_doc):
        print(tj_name)
        client.download_file("fcncloudml", f"{tj_name}/output/model.tar.gz", "./model.tar.gz")

        tar = tarfile.open("./model.tar.gz", "r:gz")

        for member in tar.getmembers():
            if member.name.endswith(".txt"):
                tar.extract(member.name)
                filename_final = format_name_logs(*tj_name_to_tuple(tj_name))
                os.replace(member.name, f"logs/{(filename_final)}.txt")
                print(f"./logs/{(filename_final)}.txt")
                break
