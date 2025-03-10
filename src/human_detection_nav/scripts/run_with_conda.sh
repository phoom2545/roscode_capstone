#!/bin/bash

# Adjust these paths according to your setup
CONDA_PATH=~/miniconda3  # or ~/miniconda3
CONDA_ENV=herobot2     # your conda environment name

# Source conda
source $CONDA_PATH/etc/profile.d/conda.sh

# Activate the environment
conda activate $CONDA_ENV

# Run the Python script
python3 $(rospack find human_detection_nav)/scripts/move_with_human_detection.py "$@"