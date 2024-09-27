#!/bin/bash

if ! [ $EUID -eq 0 ]; then
    echo "Run as sudo"
    exit -1
else
    systemctl stop jupyterhub
    docker rmi -f bash-python-r
    systemctl stop docker
    systemctl stop docker.socket
    rm -rf /opt/jhub/
fi
