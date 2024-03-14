#!/bin/bash
## copy this file to: /etc/profile.d/

## List of users with sudo access
sudo_users=$(cat /etc/group | grep sudo | cut -d: -f 4 | tr ',' ' ')

if [[ " ${sudo_users[@]} " =~ " ${USER} " ]]; then
    cat << "EOF"

╔════════════════════  Admin  ═══════/etc/profile.d/pharma_admin.sh ════╗
║             (Please prefix all commands here with 'sudo')             ║
║   ─────────────────────────────── General ─────────────────────────   ║
║    Add user: "add_new_pharma_user.sh"                                 ║
║   ──────────────────────────── Jupyter ────────────────────────────   ║
║  General: "systemctl stop/start/restart/status jupyterhub"            ║
║     Edit: "/opt/jupyterhub/jupyterhub-pharma253/jupyterhub_config.py" ║
║           (then restart jupyterhub)                                   ║
║   ──────────────────────────── Docker ─────────────────────────────   ║
║     General: "docker stats"        (usage and resources of all users) ║
║    List all: "docker ps -a"                      (started or stopped) ║
║     Stop/rm: "docker start/stop/rm jupyter-<user>" (files unaffected) ║
║  Stats/Logs: "docker stats/logs jupyter-<user>"                       ║
║ Modify live: "docker stop jupyter-<user>"                             ║
║              "docker update --memory 10g --cpus 10 jupyter-<user>"    ║
║              "docker start jupyter-<user>"                            ║
║    Stop all: "docker container rm $(sudo docker ps -a -q)"            ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
fi
