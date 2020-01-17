import numpy as np
# from np.random import Generator, PCG64, SeedSequence
# from numpy.random import default_rng
import argparse      # for command-line arguments

#class Status(Enum):
UNBURNT = 0
SMOLDERING = 1
BURNING = 2
BURNT = 3

# random number generator for checking fire spreading
# rng = np.random.Generator(PCG64)
# rng = default_rng(12345694)


def initialize_forest(size):
    forest = np.empty( (size, size), dtype='u4')
    forest.fill(UNBURNT)
    return forest


def light_tree(row_size, forest, x, y):
    # note that indexes into numpy arrays must be integers
    if x >= row_size or y >= row_size :
        print("Warning: starting position out of bounds; using center")
        i = int(row_size/2)
        j = int(row_size/2)
    else:
        i = int(x)
        j = int(y)

    forest[i,j] = SMOLDERING

def fire_spreads(prob_spread):

    prob = np.random.random_sample()
    printf("probability : " + prob)

    if prob < prob_spread:
        return True
    else:
        return False

def forest_burns(forest, prob_spread):
    fire_spreads(prob_spread)
    for index, value in np.ndenumerate(forest):
        # print(forest[index], value) #debug
        if forest[index] == SMOLDERING:
            print(index, " SMOLDERING")
            forest[index] = BURNING


def forest_is_burning(forest):
    for row in forest:
        for tree in row:
            if tree == SMOLDERING or tree == BURNING:
                return True
    return False

def print_forest(forest):
    for row in forest:
        rowStr = ''
        for tree in row:
            if tree == BURNT:
                rowStr = rowStr + '.'
            elif tree == UNBURNT:
                rowStr = rowStr + 'Y'
            elif tree == SMOLDERING:
                rowStr = rowStr + 'S'
            else:
                rowStr = rowStr + 'B'

        print(rowStr)
    print('\n')


def main():
    # process command line arguments
    # see https://docs.python.org/3.3/howto/argparse.html#id1
    parser = argparse.ArgumentParser()
    parser.add_argument("numTreesPerRow", help="number of trees in row of square grid")
    parser.add_argument("probabilityOfSpread", help="probability of fire spreading from one burning tree to a non-burning tree next to it (percent between 0 and 1)")
    # TODO: add optional arguments for i, j position of starting tree
    args = parser.parse_args()

    row_size = int(args.numTreesPerRow)
    prob_spread = float(args.probabilityOfSpread)

    forest = initialize_forest(row_size)

    percent_burned = 0.0
    # for now start burning at midlle tree
    middle_tree_index = int(row_size/2)
    light_tree(row_size, forest, middle_tree_index, middle_tree_index)

    if forest_is_burning(forest):
        print("burning")
        forest_burns(forest, prob_spread)

    print_forest(forest)


########## Run the main function
main()
