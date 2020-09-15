import re
import argparse
import json
import sys
import statistics

def main():

    time_data = json.load(sys.stdin)
    sum_of_epochs_time = 0.0
    sum_of_validations_time = 0.0
    n_epochs = len(time_data["epochs"])
    sum_of_steps_time = 0.0
    n_steps = 0
    steps_times = []
    
    for ek, ev in time_data["epochs"].items():
        if 'validation_time' in ev:
            v_time = ev["validation_time"]
        else:
            print(ev) 
            sys.exit(0)
        e_time = ev["epoch_time"]
        sum_of_epochs_time += e_time
        sum_of_validations_time += v_time
        for ik, iv in ev["steps"].items():
            steps_times.append(iv)
            sum_of_steps_time += iv
            n_steps += 1

    total_time = time_data["total_training"]
    init_time = time_data["init"]
    fit_time = time_data["fit_time"]
    model_save_time = time_data["write_model_time"]
    print("Model save time: {:.6f}".format(model_save_time))
    print("Fit function time: {:.6f}".format(fit_time))
    print("Total training time: {:.6f}".format(total_time))
    print("Largest real time delta: {:.6f}".format(time_data["largest_real_time_delta"]))
    print(" - {:.2f} % of the total training time.".format(100*time_data["largest_real_time_delta"]/total_time))
    print("Initialization time: {:.6f}".format(init_time))
    print(" - {:.2f} % of the total training time.".format(100*init_time/total_time))
    print("Epochs")
    print("  Number of epochs: {:.6f}".format(n_epochs))
    print("  Total time spent on epochs: {:.6f}".format(sum_of_epochs_time))
    print("    - {:.2f} % of the total training time.".format(100*sum_of_epochs_time/total_time))
    print("  Average epoch time: {:.6f}".format(sum_of_epochs_time/n_epochs))
    print("Validations")
    print("  Total time spent on validations: {:.6f}".format(sum_of_validations_time))
    print("    - {:.2f} % of the total training time.".format(100*sum_of_validations_time/total_time))
    print("  Average validation time: {:.6f}".format(sum_of_validations_time/n_epochs))
    print("Steps")
    print("  Number of steps: {:.6f}".format(n_steps))
    print("  Average number of steps per epoch: {:.6f}".format(float(n_steps)/float(n_epochs)))
    print("  Total time spent on steps: {:.6f}".format(sum_of_steps_time))
    print("    - {:.2f} % of the total training time.".format(100*sum_of_steps_time/total_time))
    avg_step_time = sum_of_steps_time/n_steps
    print("  First step time: {:.6f}".format(steps_times[0]))
    print("  Average step time: {:.6f}".format(avg_step_time))
    TMiIavg=(sum_of_steps_time-steps_times[0])/(n_steps-1)
    print("  Time spent on steps (without first step): {:.6f}".format(sum_of_steps_time-steps_times[0]))
    print("  T Mi Iavg: {:.6f}".format(TMiIavg))
    print("  Outstanding step times: > 1.2x the average time")
    for ek, ev in time_data["epochs"].items():
        for ik, iv in ev["steps"].items():
            if iv > 1.2 * avg_step_time:
                print ("    - Epoch({}) Step({}) Time({:.3f}) - {:.2f} times larger than average".format(ek,ik,iv,iv/avg_step_time))
    print("Beta: {:.2f} %".format(100*(sum_of_validations_time+steps_times[0])/(sum_of_steps_time-steps_times[0])))
    print("  - Validations + 1st step time = {:.6f}".format(sum_of_validations_time+steps_times[0]))
    print("  - Remaining steps time = {:.6f}".format(sum_of_steps_time-steps_times[0]))
    print("T Mi Iavg prediction errors")
    if len(steps_times) >= 2:
        print("  - Step 2 of epoch 1: {:.6f} - Estimated time: {:.6f} - Error: {:.2f} %".format(steps_times[1],steps_times[1]*(n_steps-1), abs(100*(steps_times[1]-TMiIavg)/TMiIavg)))
        if len(steps_times) >= 5:
            avg_steps_2_6 = statistics.mean(steps_times[1:6])
            print("  - Avg steps 2-6: {:.6f} - Estimated time: {:.6f} - Error: {:.2f} %".format(avg_steps_2_6,avg_steps_2_6 * (n_steps-1), abs(100*(avg_steps_2_6-TMiIavg)/TMiIavg)))
            if len(steps_times) >= 10:
                avg_steps_2_11 = statistics.mean(steps_times[1:11])
                print("  - Avg steps 2-11: {:.6f} - Estimated time: {:.6f} - Error: {:.2f} %".format(avg_steps_2_11,avg_steps_2_11*(n_steps-1),abs(100*(avg_steps_2_11-TMiIavg)/TMiIavg)))

if __name__ == "__main__":
    main()
