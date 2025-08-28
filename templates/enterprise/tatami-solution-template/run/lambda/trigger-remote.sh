#!/bin/sh
if [[ -z $1 ]];
then
    echo "Please provide the friendly name of the remote Lambda function to trigger."
    exit 1
fi
TMPFILE=$(mktemp)
aws lambda invoke \
    --invocation-type RequestResponse \
    --function-name "$1" \
    --payload file://payload.json \
    --cli-binary-format raw-in-base64-out \
    "$TMPFILE"
cat "$TMPFILE"
