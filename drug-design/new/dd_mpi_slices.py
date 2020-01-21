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
    # set up MPI and retrieve basic data
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            #number of the process running the code
    numProcesses = comm.Get_size()  #total number of processes running
    myHostName = MPI.Get_processor_name()  #machine name running the code

    start = MPI.Wtime() # start timer

    # parse command-line args...
    parser = argparse.ArgumentParser(
        description="CSinParallel Drug Design simulation - mpi4py, scored by slices of ligand list")
    parser.add_argument('maxLigand', metavar='max-length', type=int, nargs='?',
        default=DFLT_maxLigand, help='maximum length of a ligand')
    parser.add_argument('nLigands', metavar='count', type=int, nargs='?',
        default=DFLT_nLigands, help='number of ligands to generate')
    parser.add_argument('protein', metavar='protein', type=str, nargs='?',
        default=DFLT_protein, help='protein string to compare ligands against')
    parser.add_argument('-verbose', action='store_const', const=True,
                        default=False, help='print verbose output')
    args = parser.parse_args()

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

        for count in range(1, numProcesses):
            # receive a result from a worker w
            stat = MPI.Status()
            result = comm.recv(source=MPI.ANY_SOURCE, status=stat)
            w = stat.Get_source() 

            # incorporate that result into maxScore and maxScoreLigands
            if result[0] > maxScore:
                maxScore = result[0]
                maxScoreLigands = result[1]
            elif result[0] == maxScore:
                maxScoreLigands = maxScoreLigands + result[1]

        # print results
        print('The maximum score is', maxScore)
        print('Achieved by ligand(s)', maxScoreLigands)
        finish = MPI.Wtime()  # end the timing
        total_time = finish - start
        print("Total Running time: {0:12.3f} sec".format(total_time))

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

        finish = MPI.Wtime()  # end the timing
        proc_time = finish - start
        print("[{}]Process running time: {0:12.3f} sec".format(id, proc_time))

main()
