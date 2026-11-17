#!/bin/bash
source config.env
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME