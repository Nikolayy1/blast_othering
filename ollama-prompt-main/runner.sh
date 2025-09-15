#!/bin/bash

#SBATCH --account=blanca-curc-gpu
#SBATCH --qos=blanca-curc-gpu
#SBATCH --partition=blanca-curc-gpu

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=1-00:00:00
#SBATCH --gres=gpu:2
#SBATCH --mem=50G

#SBATCH --mail-user=niklas.hofstetter@colorado.edu
#SBATCH --mail-type=ALL
#SBATCH --job-name=annotate_data
#SBATCH --output=logs/data.%j.log

source ~/.bashrc

module load anaconda
conda activate bt_2025  # activate the conda environment with ollama installed

mkdir -p "$SLURM_SCRATCH/cache/HF"

export HF_HOME="$SLURM_SCRATCH/cache/HF"
export PYTHONPATH=/scratch/alpine/niho8409/blast_othering/ollama-prompt-main

echo "Starting up Ollama server"  # and redirecting output to a log file to currently running directory
nohup ollama serve > ollama_log_3.txt 2>&1 &

echo "Waiting for Ollama server to start"
sleep 1m

host_ip=$(hostname -i)
python3 -m ollama_prompt_main.run --host $host_ip --port 9999 --config default.yaml