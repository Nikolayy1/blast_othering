#!/bin/bash

#SBATCH --account=blanca-blast-lecs
#SBATCH --qos=blanca-blast-lecs
#SBATCH --partition=blanca-blast-lecs

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=48G
#SBATCH --time=24:00:00
#SBATCH --output=slurm_%j.out

#SBATCH --mail-user=niklas.hofstetter@colorado.edu
#SBATCH --mail-type=ALL
#SBATCH --job-name=annotate

source ~/.bashrc

module load anaconda
conda activate bt_2025_models

python model_testing.py