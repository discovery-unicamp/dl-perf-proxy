import sys
import argparse
import json
import statistics
import matplotlib.pyplot as plt

def plot_step_times_per_epoch(time_data, chart_title, output_filename):

    # For each epoch
    fig, axs = plt.subplots(2)
    TMiIavg = None
    n_steps = 0
    for ek, ev in time_data["epochs"].items():
        v_time = ev["validation_time"]
        e_time = ev["epoch_time"]
        x_values = []
        y_values = []
        for ik, iv in ev["steps"].items():
            y_values.append(float(iv))
            x_values.append(float(ik))
            if TMiIavg == None: TMiIavg = 0 # Skip first step
            else: TMiIavg += iv
            n_steps += 1
        axs[0].plot(x_values,y_values,label="Epoch {}".format(ek))
        axs[1].plot(x_values,y_values,label="Epoch {}".format(ek))
    TMiIavg = TMiIavg / (n_steps-1)
    axs[0].set(xlabel='step index', ylabel='execution time (s)', title=chart_title)
    axs[1].set(xlabel='step index', ylabel='execution time (s)'),
    axs[0].grid()
    box = axs[0].get_position()
    axs[0].set_position([box.x0, box.y0, box.width * 0.8, box.height])
    axs[1].set_position([box.x0, box.y0-0.9*box.height, box.width * 0.8, box.height * 0.5])
    axs[1].set_ylim(TMiIavg/1.1,TMiIavg*1.1)
    axs[1].grid()
    y_values = [TMiIavg] * len(x_values)
    axs[1].plot(x_values, y_values, ':r', label='T Mi Iavg')

    axs[1].legend(loc='center left', bbox_to_anchor=(1, 2),fontsize=8)

    if output_filename == None:
        plt.show()
    else:
        fig.savefig("{}".format(output_filename))
    plt.close(fig)



def main():

    default_chart_title="Steps execution time"
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-o', type=str, dest='output',
                        help="Defines the output file name. If not defined, the chart will be displayed on screen.")
    parser.add_argument('-t', type=str, dest='title', default=default_chart_title,
                        help="Defines the chart title. Default value = \"{}\".".format(default_chart_title))
    args = parser.parse_args()

    time_data = json.load(sys.stdin)
    plot_step_times_per_epoch(time_data, args.title, args.output)
    return 

if __name__ == "__main__":
    main()
