#!/bin/bash

if ! [ $EUID -eq 0 ]; then
    echo "Run as sudo"
    return -1
else
    systemctl stop jupyterhub
    docker rmi -f bash-python-r
    systemctl stop docker
    systemctl stop docker.socket
    ufw delete 4
    ufw delete 4
    ufw delete 4
    ufw delete 4
    ufw status
    rm -rf /opt/jhub/
fi