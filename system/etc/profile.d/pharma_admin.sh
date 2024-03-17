#!/bin/bash

## List of users with sudo access
sudo_users=$(cat /etc/group | grep sudo | cut -d: -f 4 | tr ',' ' ')

RST='\o033[0m'
YLW='\o033[1;33m'
PPL='\o033[1;35m'
CYN='\o033[1;36m'
GRN='\o033[1;32m'

if [[ " ${sudo_users[@]} " =~ " ${USER} " ]]; then
    cat << "EOF" | sed "s|%C|${CYN}|g;s|%R|${RST}|g;s|%G|${GRN}|g;s|%P|${PPL}|g;s|%Y|${YLW}|g"

  %C╔══%R %YAdmin%R %C═════════%R %Y/etc/profile.d/pharma_admin.sh%R %C════════════════╗%R
  %C║%R            Please prefix all commands here with 'sudo'           %C║%R
  %C║%R   ──── %CGeneral%R ────────────────────────────────────────────────  %C║%R
  %C║%R    %PAdd user%R: %Gadd_new_pharma_user.sh%R                              %C║%R
  %C║%R   ──── %CJupyter%R ────────────────────────────────────────────────  %C║%R
  %C║%R     %PGeneral%R: %Gsystemctl stop/start/restart/status jupyterhub%R      %C║%R
  %C║%R        %PEdit%R: %Gcd /opt/jupyterhub/jupyterhub-pharma253%R             %C║%R
  %C║%R              %Gnano jupyterhub_config.py%R                           %C║%R
  %C║%R              (then restart jupyterhub)                           %C║%R
  %C║%R   ──── %CDocker%R ─────────────────────────────────────────────────  %C║%R
  %C║%R     %PGeneral%R: %Gdocker stats%R    (usage and resources of all users)  %C║%R
  %C║%R    %PList all%R: %Gdocker ps -a%R                  (started or stopped)  %C║%R
  %C║%R     %PStop/rm%R: %Gdocker start/stop/rm jupyter-<user>%R                 %C║%R
  %C║%R              (saved files are unaffected)                        %C║%R
  %C║%R  %PStats/Logs%R: %Gdocker stats/logs jupyter-<user>%R                    %C║%R
  %C║%R %PModify live%R: %Gdocker update --memory 10g --cpus 10 jupyter-<user>%R %C║%R
  %C║%R    %PStop all%R: %Gdocker container rm $(sudo docker ps -a -q)%R         %C║%R
  %C╚══════════════════════════════════════════════════════════════════╝%R

EOF
fi