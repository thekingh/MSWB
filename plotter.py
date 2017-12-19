import numpy as np
import matplotlib.pyplot as plt
import sys
import math

def plot_data(data):

    fig, ax1 = plt.subplots()
    ax1.plot(data['i'], data['h'], "b-")
    ax1.set_xlabel("Trial #")
    ax1.set_ylabel("Happiness Rating 0-100", color="b")
    ax1.tick_params('y', colors='b')
    ax1.set_ylim([0, 100])

    ax2 = ax1.twinx()
    ax2.plot(data['i'], data['w'], "g-")
    ax2.set_ylabel("Wallet ($)", color="g")
    ax2.tick_params('y', colors="g")

    lo = 0
    hi = max(data['w'] * 1.5)
    ax2.set_ylim([lo, hi])

    plt.show()

def get_SD(data):
    num_data = len(data)
    mean     = (sum(data)) / num_data

    sum_sq_diff = 0
    for i in range(num_data):
        sum_sq_diff += pow((data[i] - mean), 2)

    return math.sqrt(sum_sq_diff/num_data)

def get_r_value(data):
    num_data = len(data)
    h_mean   = (sum(data['h']))/num_data
    e_mean   = (sum(data['w']))/num_data

    sum_h_diff_sq = 0
    sum_e_diff_sq = 0
    sum_eh   = 0
    for i in range(num_data):
        h_i = data['h'][i]
        e_i = data['w'][i]

        sum_h_diff_sq += pow(h_i - h_mean, 2)
        sum_e_diff_sq += pow(e_i - e_mean, 2)
        sum_eh += (h_i - h_mean) * (e_i - e_mean)

    return sum_eh / math.sqrt(sum_h_diff_sq * sum_e_diff_sq)


def print_stats(data):
    print("----- Simulation Stats ------")
    print("Number Trials:  ", max(data['i']))
    print("Min Happiness:  ", min(data['h']))
    print("Max Happiness:  ", max(data['h']))
    print("Avg Happiness:  ", (sum(data['h'])/len(data)))
    print("Happiness SD:   ", get_SD(data['h']))
    print("Earn vs H r =   ", get_r_value(data))
    print("Total earnings: ", data['w'][-1])

def main():
    data = np.genfromtxt(sys.argv[1], delimiter=",", skip_header=1,
                         names=["i", "cr", "ev", "rpe", "h", "w"])

    plot_data(data)
    print_stats(data)

if __name__ == "__main__":
    main()


