#!/bin/sh
curl \
    --noproxy localhost \
    -H "Content-Type: application/json"  \
    -d @payload.json \
    http://localhost:6559/2015-03-31/functions/function/invocations
