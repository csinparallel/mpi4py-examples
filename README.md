# mpi4py examples

Code examples that illustrate the use of message passing in python using the mpiy4pi library.

The folder called fire has a simple simulation of the spread of a wildfire in a forest.

The folder called drug-design contains two versions of a simple model for matching ligands to proteins.

1. dd_mpi_dynamic.py uses dynamic load balancing, assigning a new ligand to each process after it finishes one.
2. dd_mpi_equal_chunks.py splits the work equally and assigns every process the same number of ligands.
