# implementation of drug design exemplar
# python3, mpi4py, introductory
# in this version, workers obtain their own ligands as needed from a work Queue
# usage on Macalester pi cluster:  python run.py dd_mpi_items.py3 4

import argparse
import math
from mpi4py import MPI

DFLT_maxLigand = 5
DFLT_nLigands = 120
DFLT_protein = "the cat in the hat wore the hat to the cat hat party"

from dd_functions import *

# main program

def main():
    start = MPI.Wtime() # start timer
    random.seed(0) # guarantees that each run uses same random number sequence

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

        # generate ligands
        ligands = []
        for l in range(args.nLigands):
            ligands.append(makeLigand(args.maxLigand))

        # determine ligands with highest score
        maxScore = -1
        maxScoreLigands = []

        for p in range(1, numProcesses):
            comm.send("ligands ready", dest=p)                        #<ready>

        activeWorkers = numProcesses - 1   # count of workers that are not done
        while len(ligands) > 0 or activeWorkers > 0:
            stat = MPI.Status()
            request = comm.recv(source=MPI.ANY_SOURCE, status=stat)   #<request>
            w = stat.Get_source()

            if len(ligands) > 0:
                comm.send(ligands.pop(), dest=w)
            else:  # no more ligands to send, so receive worker results
                comm.send("", dest=w)
                results = comm.recv(source=w)                         #<finish>
                comm.send("DONE", dest=w)
                activeWorkers = activeWorkers - 1
                if results[0] > maxScore:
                    maxScore = results[0]
                    maxScoreLigands = results[1]
                elif results[0] == maxScore:
                    maxScoreLigands = maxScoreLigands + results[1]

        # print results
        print('The maximum score is', maxScore)
        print('Achieved by ligand(s)', maxScoreLigands)

        finish = MPI.Wtime()  # end the timing
        total_time = finish - start
        print("Total Running time: {0:12.3f} seconds".format(total_time))


    else:       # worker

        readyMsg = comm.recv(source=0)                                #<ready>
        maxScore = -1
        maxScoreLigands = []

        while True:
            comm.send("request ligand", dest=0)                       #<request>
            lig = comm.recv(source=0)
            if lig == "":
                break
            # ligand was successfully received
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

        # no more ligands to score
        comm.send([maxScore, maxScoreLigands], dest=0)                #<finish>
        doneMsg = comm.recv(source=0)

        proc_time = MPI.Wtime() - start
        print("Process {0} Running time: {1:12.3f} seconds".format(id, proc_time))


main()
