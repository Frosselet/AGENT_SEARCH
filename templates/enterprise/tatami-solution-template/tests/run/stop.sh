#!/bin/sh
docker stop $1
docker rm --force $1
