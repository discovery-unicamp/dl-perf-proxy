import yaml
import re
import argparse
import calculate_costs 


parser = argparse.ArgumentParser(description='YAML Filename')
parser.add_argument('--filename', 
                    help='yaml filename')

args = parser.parse_args()
print(args.filename)


with open(args.filename, 'r') as f:
    yaml_read = yaml.safe_load(f.read())

for yaml_list_key in yaml_read:
    print(yaml_list_key)
    yaml_list = yaml_read[yaml_list_key]
    target_pattern = yaml_list["target-pattern"]
    batch_pattern = yaml_list["batch-pattern"]
    instance_pattern = yaml_list["instance-pattern"]
    operation = yaml_list.get("operation", None)
    target_dir = yaml_list["target-dir"]
    is_markdown = yaml_list.get("is_markdown", False)


    calculate_costs.costs = calculate_costs.initial_costs.copy()
    calculate_costs.make_operation_costs(operation, calculate_costs.costs)

    bests = calculate_costs.get_pricing(target_pattern, target_dir, instance_pattern, calculate_costs.costs) 
    bests = calculate_costs.get_best_instances_for_batch(bests, batch_pattern)
    if is_markdown:
        print("|Instância",end='')

        for batch in sorted(list(bests.keys()),key=int):
            print("|"+batch,end='')
        print("|")
        for batch in sorted(list(bests.keys()),key=int):
            print("|:-:",end='')
        print("|:-:|")
        table = []
        for batch in sorted(list(bests.keys()),key=int):
            table.append(list(map(lambda x: (re.findall(instance_pattern,x[0])[0] ,x[1]) , bests[batch])))
            table[-1].sort(key=lambda x: x[0])
        
        for i,_ in enumerate(table[0]):
            print(f"|{table[0][i][0]}", end='|')
            print('|'.join([("%.2f"%(l[i][1])) for l in table]) + '|')
            #instance, value = bests[batch][0] 
            #instance = re.findall(instance_pattern, instance)[0]
           # print(f"{instance} - {value:.2f}") 
    else:
        table = []
        for batch in sorted(list(bests.keys()),key=int):
            table.append(list(map(lambda x: (re.findall(instance_pattern,x[0])[0] ,x[1]) , bests[batch])))
            table[-1].sort(key=lambda x: x[0])
        
        for i,_ in enumerate(table[0]):
            print(f"{table[0][i][0]}", end=',')
            print(','.join([("%f"%(l[i][1])) for l in table]) )

    print(sum([sum([k[1] for k in bests[x]]) for x in bests]) * 3)

    

