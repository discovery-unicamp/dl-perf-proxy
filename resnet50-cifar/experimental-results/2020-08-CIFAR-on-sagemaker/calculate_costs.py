import re
import os
import glob
import sys

initial_costs = {
    "p2-1": 0.9,
    "p2-8": 7.2,
    "p2-16": 14.4,
    "p3-1": 3.06,
    "p3-4": 12.24,
    "p3-8": 24.48,
    "g4dnxlarge-1": 0.526,
    "g4dn2xlarge-1": 0.752,
    "g4dn4xlarge-1": 1.204,
    "g4dn8xlarge-1": 2.176,
    "g4dn16xlarge-1": 4.352,
    "g4dn12xlarge-4": 3.912
}

costs = {}

def make_operation_costs(operation = None, costs=costs):
    operations = {
            'one': (lambda x: 1),
            'to_seconds': (lambda x: x/3600),
            }
    if operation:
        if operation not in operations:
            print(f"operation not founded, avaiable: {' '.join(list(operations.keys()))}")
            sys.exit(1)
            return 
        for i in costs:
            costs[i] = operations[operation](costs[i])

def reset_costs():
    costs = initial_costs.copy()


def get_pricing(metric, directory, instance_metric=r'', costs=costs):
    prices = {}
    for i in glob.glob(directory):
        with open(i) as f:
            file_read = f.read()    
            instance = re.findall(instance_metric, i)

            if instance:
                instance = instance[0]
            else:
                print("instance metric not working")
                print("founded:", instance)
                print("used:", i)
                print("metric:", instance_metric)
                sys.exit(1)
            
            target = re.findall(metric, file_read)
            if target:
                target = float(target[0])
            else:
                print("target metric not working")
                print("founded:", target)
                print("used:", i)
                print("metric:", metric)
                sys.exit(1)
            prices[i] =  (float(target) * costs[instance])  
    return prices

def get_best_instances_for_batch(prices, batch_metric):
    prices_ord = {}
    for instance in prices.keys():
        batch = re.findall(batch_metric, instance)
        if batch:
            batch = batch[0] 
        else: 
            print("batch metric not working")
            print("founded:", batch)
            print("used:", instance)
            print("metric:", batch_metric)
            sys.exit(1)
        if batch in prices_ord:
            prices_ord[batch].append((instance, prices[instance]))
        else:
            prices_ord[batch] = [(instance, prices[instance])]
    for batch in prices_ord.keys():
        prices_ord[batch].sort(key=lambda x: x[1])
    return prices_ord
     

if __name__ == "__main__":
    for i in initial_costs:
        print(i,initial_costs[i],sep=',')
