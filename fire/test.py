import argparse      # for command-line arguments
import matplotlib.pyplot as plt
import math
import time
from mpi4py import MPI

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

    return [row_size, prob_spread_increment, num_trials]


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
    # MPI information
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            #number of the process running the code
    numProcesses = comm.Get_size()  #total number of processes running
    myHostName = MPI.Get_processor_name()  #machine name running the code

    if id == 0:
        start = MPI.Wtime() # start the timing
    # master process will get the arguments
    # each process gets sent row_size, prob_spread_increment, and
    # its number of trials to perform (via a broadcast)
    if id == 0:
        # row_size, prob_spread_increment, tot_num_trials = parseArguments()
        args = parseArguments()
        print(args) #debug
    else:
        args = None

    # all processes participate in the broadcast
    sim_data = comm.bcast(args, root=0)
    print("proc {} has args: {}".format(id, sim_data))
    row_size = sim_data[0]
    prob_spread_increment =sim_data[1]
    tot_num_trials = sim_data[2]

    # determine number of trials that each process will do
    # by checking whether trials are divisible by number of processes
    # and if not spreading the work so that some do one extra trial
    remainder = tot_num_trials%numProcesses
    num_trials = int(tot_num_trials/numProcesses)
    if remainder !=0 and id >= numProcesses - remainder:
        num_trials += 1
    print("proc {} has num trials: {}".format(id, num_trials))

########## Run the main function
main()
