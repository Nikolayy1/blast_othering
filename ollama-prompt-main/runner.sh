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
PORT = 9999

# --- Cleanup: Kill old Ollama if it exists ---
echo "Cleaning up old Ollama processes..."
pkill -f "ollama serve" || true
sleep 3

echo "Starting up Ollama server"
nohup ollama serve --port $PORT > ollama_log_annotation.txt 2>&1 &

# --- Verify it’s running ---
echo "Verifying Ollama is running..."
if ss -tlnp | grep -q ":$PORT"; then
    echo "✅ Ollama server is running on port $PORT"
else
    echo "❌ Ollama failed to start, exiting."
    exit 1
fi

# --- Verify Model Exists ---
echo "Checking available models..."
ollama list || true

# --- Run Your Annotator ---
echo "Starting annotation..."
python3 -m ollama-prompt-main.run \
    --host 127.0.0.1 \
    --port $PORT \
    --config default.yaml

echo "✅ Job completed successfully."