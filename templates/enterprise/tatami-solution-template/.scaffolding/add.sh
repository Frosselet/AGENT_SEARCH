#!/bin/sh

# Launch scaffolding process

if ! command -v python &> /dev/null; then
    echo "[INFO] 'python' command could not be found, use 'python3' instead"
    python3 ./.scaffolding/add.py
else
    python ./.scaffolding/add.py
fi
