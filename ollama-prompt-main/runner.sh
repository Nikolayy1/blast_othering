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

unset OLLAMA_ORIGINS
export OLLAMA_HOST=127.0.0.1  # Localhost only, since same node


echo "Starting up Ollama server"
nohup ollama serve --port 9999 > ollama_log_annotation.txt 2>&1 &

echo "Waiting for Ollama server to start..."
for i in {1..12}; do
    if curl -s http://127.0.0.1:9999/api/tags >/dev/null; then
        echo "✅ Ollama is up"
        break
    fi
    echo "⏳ Waiting ($i/12)..."
    sleep 10
done

ss -tlnp | grep 9999 || echo "⚠️ Ollama not listening yet"

echo "Running annotation script"
python3 -m ollama-prompt-main.run --host 127.0.0.1 --port 9999 --config default.yaml