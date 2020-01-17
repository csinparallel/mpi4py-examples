# implementation of drug design exemplar
# python3, mpi4py, introductory
# usage on Macalester pi cluster:  python run.py dd_mpi_slices.py3 4

import string
import random
import math
from mpi4py import MPI

maxLigand = DEFAULT_max_ligand = 5
nLigands = DEFAULT_nligands = 120
protein = DEFAULT_protein = \
    "the cat in the hat wore the hat to the cat hat party"

# function makeLigand
#   1 argument:  maximum length of a ligand
#   return:  a random ligand string of random length between 1 and arg1

def makeLigand(maxLength):
    len = random.randint(1, maxLength)
    ligand = ""
    for c in range(len):
        ligand = ligand + string.ascii_lowercase[random.randint(0,25)]
    return ligand

# function score
#   2 arguments:  a ligand and a protein sequence
#   return:  int, simulated binding score for ligand arg1 against protein arg2

def score(lig, pro):
    if len(lig) == 0 or len(pro) == 0:
        return 0
    if lig[0] == pro[0]:
        return 1 + score(lig[1:], pro[1:])
    else:
        return max(score(lig[1:], pro), score(lig, pro[1:]))

#def worker(q, ligandList):


# main program

random.seed(0) # guarantees that each run uses the same random number sequence
# parse command-line args...

# set up MPI and retrieve basic data
comm = MPI.COMM_WORLD
id = comm.Get_rank()            #number of the process running the code
numProcesses = comm.Get_size()  #total number of processes running
myHostName = MPI.Get_processor_name()  #machine name running the code

if numProcesses > 1:
    if id == 0:    # master
       
        # generate ligands
        ligands = []
        for l in range(nLigands):
            ligands.append(makeLigand(maxLigand))

        # determine ligands with highest score
        maxScore = -1
        maxScoreLigands = []

        n = math.ceil(len(ligands)/numProcesses) # ligands per worker
        for p in range(1, numProcesses):
            comm.send(ligands[(p-1)*n:p*n], dest=p)

        for p in range(1, numProcesses):
            received = comm.recv(source=p)
            if received[0] > maxScore:
                maxScore = received[0]
                maxScoreLigands = received[1]
            elif received[0] == maxScore:
                maxScoreLigands = maxScoreLigands + received[1]

        # print results
        print('The maximum score is', maxScore)
        print('Achieved by ligand(s)', maxScoreLigands)

    else:       # worker
        
        ligandList = comm.recv(source=0)
        maxScore = -1
        maxScoreLigands = []

        for lig in ligandList:
            s = score(lig, protein)
            if s > maxScore:
                maxScore = s

                maxScoreLigands = [lig]
                print("\n[", id, "]-->new maxScore ", s, sep='') # show progress
                print("[", id, ']', lig, ', ',
                      sep='', end='', flush=True) # show progress
            elif s == maxScore:
                maxScoreLigands.append(lig)
                print("[", id, ']', lig, ', ',
                      sep='', end='', flush=True) # show progress
            
        print()  # show progress
        comm.send([maxScore, maxScoreLigands], dest=0)

