# implementation of drug design exemplar
# python3, mpi4py, introductory
# this version assigns each worker a slice of the list of ligands to score
# usage on Macalester pi cluster:  python run.py dd_mpi_slices.py3 4

import string
import argparse
import math
from mpi4py import MPI

from dd_functions import *

DFLT_maxLigand = 5
DFLT_nLigands = 120
DFLT_protein = "the cat in the hat wore the hat to the cat hat party"

# main program

def main():
    start = comm.Wtime()

    # parse command-line args...
    parser = argparse.ArgumentParser(
        description="CSinParallel Drug Design simulation - sequential")
    parser.add_argument('maxLigand', metavar='max-length', type=int, nargs='?',
        default=DFLT_maxLigand, help='maximum length of a ligand')
    parser.add_argument('nLigands', metavar='count', type=int, nargs='?',
        default=DFLT_nLigands, help='number of ligands to generate')
    parser.add_argument('protein', metavar='protein', type=str, nargs='?',
        default=DFLT_protein, help='protein string to compare ligands against')
    parser.add_argument('-verbose', action='store_const', const=True,
                        default=False, help='print verbose output')
    args = parser.parse_args()

    # set up MPI and retrieve basic data
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            #number of the process running the code
    numProcesses = comm.Get_size()  #total number of processes running
    myHostName = MPI.Get_processor_name()  #machine name running the code

    if numProcesses <= 1:
        print("Need at least two processes, aborting")
        return

    # assert - numProcesses > 1
    if id == 0:    # master
        random.seed(0) # guarantees each run uses same random number sequence

        # generate ligands
        ligands = []
        for l in range(args.nLigands):
            ligands.append(makeLigand(args.maxLigand))

        # determine ligands with highest score
        maxScore = -1
        maxScoreLigands = []

        n = math.ceil(len(ligands)/numProcesses) # ligands per worker
        for p in range(1, numProcesses):
            comm.send(ligands[(p-1)*n:p*n], dest=p)

        for p in range(1, numProcesses):
            stat = MPI.Status()
            received = comm.recv(source=MPI.ANY_SOURCE, status=stat)
            w = stat.Get_source()

            if received[0] > maxScore:
                maxScore = received[0]
                maxScoreLigands = received[1]
            elif received[0] == maxScore:
                maxScoreLigands = maxScoreLigands + received[1]

        # print results
        print('The maximum score is', maxScore)
        print('Achieved by ligand(s)', maxScoreLigands)
        finish = comm.Wtime()
        print('Overall time is', finish - start)

    else:       # worker

        ligandList = comm.recv(source=0)
        maxScore = -1
        maxScoreLigands = []

        for lig in ligandList:
            s = score(lig, args.protein)
            if s > maxScore:
                maxScore = s

                maxScoreLigands = [lig]
                printIf(args.verbose, "\n[{}]-->new maxScore {}".format(id, s))
                printIf(args.verbose, "[{}]{}, ".format(id, lig),
                        end='', flush=True) 
            elif s == maxScore:
                maxScoreLigands.append(lig)
                printIf(args.verbose, "[{}]{}, ".format(id, lig),
                    end='', flush=True) 
        
        printIf(args.verbose)  # print final newline
        comm.send([maxScore, maxScoreLigands], dest=0)
        finish = comm.Wtime()
        print('[{}] time is {}'.format(id, finish - start))

main()
