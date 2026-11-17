#!/bin/bash


source config.env

if docker container inspect "$CONTAINER_NAME" > /dev/null 2>&1; then
      echo "Container already exists."
      echo "Stopping and removing the existing container..."
      docker stop $CONTAINER_NAME
      docker rm $CONTAINER_NAME
fi

echo "Container: $CONTAINER_NAME"
echo "VNC URL: http://localhost:6080/vnc.html"

docker run -it \
    --name $CONTAINER_NAME \
    --init \
    --shm-size=1g \
    -p 127.0.0.1:6080:6080 \
    -e DISPLAY=:1 \
    -e QT_X11_NO_MITSHM=1 \
    -e LIBGL_ALWAYS_SOFTWARE=1 \
    $IMAGE_NAME