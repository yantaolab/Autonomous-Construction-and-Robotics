#!/bin/bash
set -e

export DISPLAY=${DISPLAY:-:1}

# 1. Start virtual X server
Xvfb $DISPLAY \
    -screen 0 1600x900x24 \
    -ac \
    +extension GLX \
    +render \
    -noreset &

# Wait for X server
for i in {1..30}; do
    if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
        break
    fi
    sleep 0.2
done

xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 || {
    echo "Failed to start Xvfb"
    exit 1
}

# 2. Start XFCE desktop
dbus-launch --exit-with-session startxfce4 \
    >/tmp/xfce.log 2>&1 &

# 3. Start VNC server
x11vnc \
    -display $DISPLAY \
    -localhost \
    -forever \
    -shared \
    -nopw \
    -rfbport 5900 \
    -bg \
    -o /tmp/x11vnc.log

# 4. Start noVNC
websockify \
    --web=/usr/share/novnc \
    6080 \
    localhost:5900 \
    >/tmp/novnc.log 2>&1 &

# 5. Initialize ROS
source /opt/ros/noetic/setup.bash

# 6. Execute container command
exec "$@"