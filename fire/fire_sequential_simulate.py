#
# Run multiple simulations of a fire burning at several probability thresholds.
#
# Ported to python from the original Shodor foundation example:
#  https://www.shodor.org/refdesk/Resources/Tutorials/BasicMPI/
#
# Libby Shoop     Macalester College
#
import argparse      # for command-line arguments
import matplotlib.pyplot as plt
import math
import time

from fire_functions import *

def parseArguments():
    """Handle command line arguments

    Run with -h to get details of each argument.

    Returns:
        A list containg each argument provided
    """
    # process command line arguments
    # see https://docs.python.org/3.3/howto/argparse.html#id1
    parser = argparse.ArgumentParser()
    parser.add_argument("numTreesPerRow", help="number of trees in row of square grid")
    parser.add_argument("probabilityIncrement", help="amount to increment the probability threshold of fire spreading for each set of probability trials")
    parser.add_argument("numberOfTrials", help="number of times to run the fire simulation with a new forest for each proability in set of probabilities")

    args = parser.parse_args()

    row_size = int(args.numTreesPerRow)
    prob_spread_increment = float(args.probabilityIncrement)
    num_trials = int(args.numberOfTrials)

    return row_size, prob_spread_increment, num_trials


def burn_until_out(row_size, forest, prob_spread):
    """ one simulation of the buring forest
    Parameters:
        row_size (int): number of trees in each row and column
        forest (array): array representing the 2D forest
        prob_spread (float):
            probability threshold for determining whether burning tree will
            spread to neighboring tree
    """

    percent_burned = 0.0
    # for now start burning at midlle tree
    middle_tree_index = int(row_size/2)
    light_tree(row_size, forest, middle_tree_index, middle_tree_index)

    iter = 0 # how many iterations before the fire burns out
    while forest_is_burning(forest):
        # print("burning") # debug
        forest_burns(forest, row_size, prob_spread)
        iter += 1

    percent_burned = get_percent_burned(forest, row_size)

    # print_forest(forest)  #debug

    return int(iter), float(percent_burned)

############################# main() ##########################
def main():

    row_size, prob_spread_increment, num_trials = parseArguments()

    start = time.process_time()
    # determine how many probabilities between .1 up to but not including 1.0
    # will be tried, based on increment given on cammand line.
    tot_prob_trials = int(math.ceil((1.0 - 0.1)/prob_spread_increment))
    # Note: num_trials simulations will be run, where an iteration
    #       will be for tot_prob_trials.
    #
    # print("total probability trials: {}".format(tot_prob_trials))  #debug
    # set up result data arrays to hold:
    #   sums of each value computed for each probability while iterating
    percent_burned_data = np.zeros( (tot_prob_trials, 2) )
    iters_per_sim_data = np.zeros( (tot_prob_trials, 2) )

    # The primary work: run the trials using each set of proabilities.
    # There will be num_trials x tot_prob_trials individual fire simulations
    # run, each with a new forest.
    for i in range(num_trials):
        idx = 0     # index into result data array
        for prob_spread in np.arange(0.1, 1.0, prob_spread_increment):
            forest = initialize_forest(row_size)
            iter, percent_burned = burn_until_out(row_size, forest, prob_spread)
            # print("Probability threshold: {}, index: {}".format(prob_spread, idx))
            # print("Iterations until fire burns out: {}".format(iter))
            # print("Percent burned: {}".format(percent_burned))

            if i > 0:
                percent_burned_data[(idx,0)] = prob_spread
                iters_per_sim_data[(idx,0)] = prob_spread
            percent_burned_data[(idx,1)] += percent_burned
            iters_per_sim_data[(idx,1)] += iter
            # print("array: {}, {}".format(percent_burned_data[(idx,0)], percent_burned_data[(idx,1)]))

            idx += 1

    # find average percent burned and number of iterations
    # for each probability threashold
    for row in range(tot_prob_trials):
        percent_burned_data[(row,1)] = percent_burned_data[(row,1)]/num_trials
        iters_per_sim_data[(row,1)] = iters_per_sim_data[(row,1)]/num_trials

        # print of data that gets plotted
        # print("prob, avg percent burned: {}, {}".\
        # format(percent_burned_data[(row,0)], percent_burned_data[(row,1)]))
        # print("prob, avg iterations per simulation: {}, {}".\
        # format(iters_per_sim_data[(row,0)], iters_per_sim_data[(row,1)]))

    finish = time.process_time()
    print("Running time: {} seconds".format(finish-start))

    # Create a figure with 2 plots of the simulation results
    upper_title = "Simulation: " + str(num_trials) + " trials for each proability\n"
    upper_title = upper_title + str(row_size) + "x" + str(row_size) + " forest"
    fig, (ax1, ax2) = plt.subplots(1, 2)  # 2 plots side by side
    fig.suptitle(upper_title)

    ax1.plot(percent_burned_data[:,0], percent_burned_data[:,1])
    ax1.set(xlabel="Probability threshold", ylabel="Avg percent burned")

    ax2.plot(iters_per_sim_data[:,0], iters_per_sim_data[:,1])
    ax2.set(xlabel="Probability threshold", ylabel="Avg iterations per simulation")

    plt.show()

########## Run the main function
main()
