import re
import argparse
import os.path
import json
import sys

def main():

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-cs', type=str, dest='computing_system', help="Name of the computing system used to train the model.", required=True)
    parser.add_argument('-bs', type=str, dest='batch_size', help="Batch size used for trainning.", required=True)
    args = parser.parse_args()
    
    all_times = parse_input_log()

    all_times["computing_system"] = args.computing_system
    all_times["batch_size"] = args.batch_size
    
    print(json.dumps(all_times,indent=4))

# Parse the a log file from stdin and returns a tuple with five values:
# 1- the initialization time (-1.0 in case it was not matched on the log file)
# 2- a dictionary mapping epoch number and step ids to step execution time.
# 3- a diction mapping epoch ids to validation time
# 4- a diction mapping epoch ids to epochs execution time
# 5- a list with all intervals (deltas) computed using the real wallclock time
def parse_input_log():

    rt_deltas = []
    validations = {}
    epochs = {}
    steps = {}
    step_pm=re.compile(r'\d+ step training time: \d+(\.\d+)?s')
    last_step_pm=re.compile(r'\d+ steps training: \d+(\.\d+)?s')
    validation_pm=re.compile(r'Validation time: \d+(\.\d+)?s')
    epoch_pm=re.compile(r'Epoch time: \d+(\.\d+)?s')
    init_pm=re.compile(r'\(\'Tempo de inicializacao: \', \d+(\.\d+)?\)')
    rt_pm=re.compile(r'Real time: \d+(\.\d+)?')
    dt_pm=re.compile(r'Tempo do fit: +\d+(\.\d+)?')
    fit_time_pm=re.compile(r'Tempo do fit: \d+(\.\d+)?')
    write_model_time_pm=re.compile(r'Tempo levado para o modelo ser salvo: \d+(\.\d+)?')
    val_acc_pm=re.compile(r'loss: \d+[.]\d+ - accuracy: \d+[.]\d+ - val_loss: \d+[.]\d+ - val_accuracy: \d+[.]\d+')
    first_rt = 0.0
    last_rt = 0.0
    epoch_id=1
    init_time = -1.0
    dt_time = -1.0
    fit_time = -1.0
    write_model_time = -1.0

    for line in sys.stdin:
            # Parse steps times
            res=step_pm.search(line)
            if res != None:
                sline = line.split()
                step_i = int(sline[0])
                step_time = float(sline[4][:-1])
                #print("step,{},{},{}".format(epoch_id,step_i,step_time))
                if epoch_id not in epochs: epochs[epoch_id] = {}
                if "steps" not in epochs[epoch_id] : epochs[epoch_id]["steps"] = {}
                epochs[epoch_id]["steps"][step_i] = step_time
            res=last_step_pm.search(line)
            if res != None:
                sline = line.split()
                step_i = int(sline[0])
                step_time = float(sline[3][:-1])
                if epoch_id not in epochs: epochs[epoch_id] = {}
                if "steps" not in epochs[epoch_id] : epochs[epoch_id]["steps"] = {}
                epochs[epoch_id]["steps"][step_i] = step_time
            # Parse validations times
            res=validation_pm.search(line)
            if res != None:
                sline = line.split()
                validation_time = float(sline[2][:-1])
                #print("validation,{},{}".format(epoch_id,validation_time))
                if epoch_id not in epochs: epochs[epoch_id] = {}
                epochs[epoch_id]["validation_time"] = validation_time
            # Parse validation accuracy
            res=val_acc_pm.search(line)
            if res != None:
                sline = line.split()
                validation_acc = float(sline[-1])
                
                if epoch_id not in epochs: epochs[epoch_id] = {}
                epochs[epoch_id]["validation_accuracy"] = validation_acc
                epoch_id = epoch_id + 1
            # Parse epochs times
            res=epoch_pm.search(line)
            if res != None:
                sline = line.split()
                epoch_time = float(sline[2][:-1])
                #print("epoch,{},{}".format(epoch_id,epoch_time))
                if epoch_id not in epochs: epochs[epoch_id] = {}
                epochs[epoch_id]["epoch_time"] = epoch_time
            # Parse initialization time
            res=init_pm.search(line)
            if res != None:
                sline = line.split()
                init_time = float(sline[4][:-1])
                #print("init,{}".format(init_time))
            # Parse "duracao do treinamento"
            res=dt_pm.search(line)
            if res != None:
                sline = line.split()
                dt_time = float(sline[3])
                #print("training duration,{}".format(dt_time))
            # Parse fit time 
            res = fit_time_pm.search(line)
            if res != None:
                sline = line.split()
                fit_time = float(sline[-1])
            # Parse time to write model
            res = write_model_time_pm.search(line) 
            if res != None:
                sline = line.split()
                write_model_time = float(sline[-1])

            # Parse real times
            res=rt_pm.search(line)
            if res != None:
                sline = line.split()
                #Handle cases in which there is an 's' suffix on the time
                if sline[2][-1] == 's': real_time = float(sline[2][:-1])
                else: real_time = float(sline[2])
                if first_rt == 0.0: first_rt = real_time
                last_rt_delta = real_time-last_rt
                if last_rt > 0.0: rt_deltas.append(last_rt_delta)
                last_rt = real_time

    all_times = {"init": init_time,
                 "total_training": dt_time,
                 "largest_real_time_delta": last_rt-first_rt,
                 "fit_time": fit_time,
                 "write_model_time": write_model_time,
                 "epochs": epochs}
    return all_times
        
if __name__ == "__main__":
    main()
