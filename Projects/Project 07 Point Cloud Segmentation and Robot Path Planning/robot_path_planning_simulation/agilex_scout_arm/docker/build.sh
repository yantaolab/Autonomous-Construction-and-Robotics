#!/bin/bash
source config.env
docker build -t ${IMAGE_NAME} -f Dockerfile .