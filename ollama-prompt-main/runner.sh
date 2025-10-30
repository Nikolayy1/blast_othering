#!/bin/bash

#SBATCH --account=blanca-blast-lecs
#SBATCH --qos=blanca-blast-lecs
#SBATCH --partition=blanca-blast-lecs

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --time=04:00:00
#SBATCH --gres=gpu:h100_3g.40gb:2
#SBATCH --mem=50G

#SBATCH --mail-user=niklas.hofstetter@colorado.edu
#SBATCH --mail-type=ALL
#SBATCH --job-name=annotate
#SBATCH --output=logs/data.%j.log

source ~/.bashrc

module load anaconda
conda activate bt_2025  # activate the conda environment with ollama installed

mkdir -p "$SLURM_SCRATCH/cache/HF"

export HF_HOME="$SLURM_SCRATCH/cache/HF"
export PYTHONPATH=/scratch/alpine/niho8409/blast_othering/ollama-prompt-main

echo "Starting up Ollama server"
nohup ollama serve --host 0.0.0.0 --port 9999 > ollama_log_annotation.txt 2>&1 &
echo "Waiting for Ollama server to start"
sleep 1m
host_ip=$(hostname -i)
echo "DEBUG: Host IP is $host_ip"
curl -s http://$host_ip:9999/api/tags || echo "⚠️ Ollama not responding on $host_ip:9999"
python3 -m ollama-prompt-main.run --host $host_ip --port 9999 --config default.yaml