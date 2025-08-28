#!/bin/sh

# Create the directory if it doesn't exist
mkdir -p "${HOME}/.aws-lambda-rie"

# Download latest 'aws-lambda-rie' and put it in local path
curl \
    -L --ssl-revoke-best-effort \
    -o "${HOME}/.aws-lambda-rie/aws-lambda-rie" \
    "https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie"

# Check the exit code of the curl command
if [ $? -ne 0 ]; then
    echo "[ERROR] 'curl' command failed, most likely due to proxy configuration not set in your system and/or terminal. See https://tat-docs.cglcloud.com/solutions/platforms/quant-for-cash/requirements.html#http_proxy-and-https_proxy for more details."
    exit 1
else
    # Check if the file exists
    if [ -e "${HOME}/.aws-lambda-rie/aws-lambda-rie" ]; then
        # Make the file executable on Unix-like systems
        if [ "$(uname)" = "Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" = "Linux" ]; then
            chmod +x "${HOME}/.aws-lambda-rie/aws-lambda-rie"
        fi

        echo "[INFO] Successfully downloaded 'aws-lambda-rie' and it is now present at '${HOME}/.aws-lambda-rie/aws-lambda-rie'."
    else
        echo "[ERROR] The file does not exist at '${HOME}/.aws-lambda-rie/aws-lambda-rie'."
        exit 1
    fi
fi
