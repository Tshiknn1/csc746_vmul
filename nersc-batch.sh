#!/bin/bash
#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q debug
#SBATCH -J csc746_f25_evan_caplinger_sum
#SBATCH --mail-user=ecaplinger@sfsu.edu
#SBATCH --mail-type=ALL
#SBATCH -t 00:10:00

#OpenMP settings:
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

#run the application:
srun -n 1 -c 1 --cpu_bind=cores build/benchmark-basic
srun -n 1 -c 1 --cpu_bind=cores build/benchmark-vectorized
srun -n 1 -c 1 --cpu_bind=cores build/benchmark-blas
srun -n 1 -c 1 --cpu_bind=cores --export=ALL,OMP_NUM_THREADS=1 build/benchmark-openmp
srun -n 1 -c 4 --cpu_bind=cores --export=ALL,OMP_NUM_THREADS=4 build/benchmark-openmp
srun -n 1 -c 16 --cpu_bind=cores --export=ALL,OMP_NUM_THREADS=16 build/benchmark-openmp
srun -n 1 -c 64 --cpu_bind=cores --export=ALL,OMP_NUM_THREADS=64 build/benchmark-openmp
