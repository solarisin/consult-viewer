# syntax=docker/dockerfile:1

FROM python:3

# Set the working directory in the container
RUN mkdir -p /opt/consult-viewer
WORKDIR /opt/consult-viewer

# needed for qt gui support from docker
ENV QT_X11_NO_MITSHM=1
ENV QT_GRAPHICSSYSTEM="native"

# Note: Adding libxcb-cursor0, libegl1, and other dependencies for PySide6 and the XCB platform plugin
# Install necessary system dependencies for running a PySide6 application
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxcb1 \
    libxrender1 \
    libxi6 \
    libdbus-1-3 \
    libxcb-cursor0 \
    libegl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./src /opt/consult-viewer/

# Create the docker user
ARG userid=1000
ARG groupid=1000
RUN mkdir -p /home/docker
RUN groupadd -g $groupid docker
RUN useradd -u $userid -g docker docker -s /bin/bash
RUN chown -R docker:docker /home/docker
RUN chown -R docker:docker /opt/consult-viewer
USER docker
ENV HOME=/home/docker

# Install PySide6 without specifying a version to get the latest
RUN pip install --upgrade pip && \
    pip install PySide6


CMD [ "python", "/opt/consult-viewer/guitest.py" ]