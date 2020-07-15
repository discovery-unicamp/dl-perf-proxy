import sys
import argparse
import json
import statistics
import matplotlib.pyplot as plt


def read_results(filename_list, ignore_first_iteration_from_epoch1):

    # results_dataset
    #    p2-1
    #       1024
    #         [
    #            {
    #              filename: fn,
    #              epochs: { 1: (time,accuracy), 2: ... }
    #            },
    #            {
    #              filename: fn,
    #              epochs: { 1: (time,accuracy), 2: ... }
    #            },
    #            ...
    #         ]
    results_dataset = {}
    
    for fn in filename_list:
        #print("Processing {}".format(fn))
        with open(fn) as json_file:
            exp_result = json.load(json_file)
            if not "computing_system" in exp_result:
                print("Experimental results from filename {} have no computing_system information. Skiping this file".format(fn))
            else:
                cs = exp_result["computing_system"]
                if not cs in results_dataset:
                    #print("Adding {} to results_dataset.compute_system".format(cs))
                    results_dataset[cs] = {}
                bs = exp_result["batch_size"]
                if not bs in results_dataset[cs]:
                    #print("Adding batch size {} to results_dataset[{}]".format(bs,cs))
                    results_dataset[cs][bs] = []

                exp_data = {}
                exp_data["filename"] = fn
                exp_data["epochs"] = {}
                for k,v in exp_result["epochs"].items():
                    epoch_id = k
                    # TODO: Do we want to remove the execution time of the first iteration from the first epoch?
                    if ignore_first_iteration_from_epoch1:
                        #print("Ignoring first iteration")
                        epoch_time = float(v["epoch_time"]) - float(v["steps"]["1"]);
                    else:
                        epoch_time = float(v["epoch_time"]);
                    epoch_accuracy = v["validation_accuracy"];
                    if not epoch_id in exp_data["epochs"]:
                        exp_data["epochs"][epoch_id] = {}
                    exp_data["epochs"][epoch_id] = (epoch_time,epoch_accuracy)

                results_dataset[cs][bs].append(exp_data)


    return results_dataset
    #exp_data = json.load()


def summarize_results_from_multiple_experiments(data):
    # results_dataset
    #    p2-1:
    #       1024:
    #          epochs: { 1: (time,accuracy), 2: ... }
    summary = {}
    for cs,cs_data in data.items():
        if not cs in summary: summary[cs] = {}
        for bs, bs_data in cs_data.items():
            if not bs in summary[cs]: summary[cs][bs] = {}
            # TODO: For each experiment, we summarize the results. For now just getting the firts one.
            summary[cs][bs] = bs_data[0]

    return summary
        
        

def plot_accuracy_vs_time(data, chart_title, output_filename):


    # For each epoch
    fig, ax = plt.subplots(1)
    n_steps = 0
    for cs, cs_data in data.items():
        for bs, bs_data in cs_data.items():
            acc_time = 0.0
            x_values = []
            y_values = []
            sorted_list = []
            for k, v in sorted(bs_data["epochs"].items(), key=lambda item: int(item[0])):
                sorted_list.append(v)
            for (epoch_time,acc) in sorted_list:
                acc_time += epoch_time
                y_values.append(float(acc))
                x_values.append(float(acc_time))

            ax.plot(x_values,y_values,label="{} - {}".format(cs,bs))
    ax.set(xlabel='Execution time', ylabel='Accuracy', title=chart_title)
    ax.grid()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1),fontsize=8)

    if output_filename == None:
        plt.show()
    else:
        fig.savefig("{}".format(output_filename))
    plt.close(fig)


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main():

    default_chart_title="Accuracy vs Execution time"
    parser = argparse.ArgumentParser(description='Generate a Accuracy vs Execution time chart for multiple experiments.')
    
    parser.add_argument('-o', type=str, dest='output',
                        help="Defines the output file name. If not defined, the chart will be displayed on screen.")

    parser.add_argument('-t', type=str, dest='title', default=default_chart_title,
                        help="Defines the chart title. Default value = \"{}\".".format(default_chart_title))

    parser.add_argument('filenames', metavar='filename', type=str, nargs='+',
                        help='a list of filenames containing the experimental results in JSON format.')

    parser.add_argument("--ignore_first_iteration", help="Ignore first iteration when computing epoch times.")
    
    args = parser.parse_args()

    # Read results - one filename per experimental results

    accuracy_vs_time_dataset = read_results(args.filenames, args.ignore_first_iteration != None)

    accuracy_vs_time_dataset = summarize_results_from_multiple_experiments(accuracy_vs_time_dataset)
    
    plot_accuracy_vs_time(accuracy_vs_time_dataset, args.title, args.output)
    
    return 

if __name__ == "__main__":
    main()
