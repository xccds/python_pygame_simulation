import matplotlib.pyplot as plt
import numpy as np
from IPython import display

plt.ion()

def plot_hist(data):

    num_bins = 10
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()

    # the histogram of the data
    plt.hist(data, num_bins, density=True)
    # Tweak spacing to prevent clipping of ylabel
    plt.show(block=False)
    plt.pause(.1)