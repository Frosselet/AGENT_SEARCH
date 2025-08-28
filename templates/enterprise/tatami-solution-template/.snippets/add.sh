#!/bin/sh

# Launch snippets process

script_dir="$(cd "$(dirname "$0")" && pwd)"
path="."

echo "Script folder: $script_dir"
echo "Target folder: $path"

if ! command -v python &> /dev/null; then
    echo "[INFO] 'python' command could not be found, use 'python3' instead"
    python3 "$script_dir/add.py" "$path"
else
    python "$script_dir/add.py" "$path"
fi
