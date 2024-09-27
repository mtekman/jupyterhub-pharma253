## Leave the first 10 lines alone.
c = get_config()  #noqa

from pathlib import Path as currpath
from sys import path as modulepath
modulepath.append(str(currpath().resolve())) ## need this to import custom module

## Custom module: DockerSystemProfileSpawner and Templates
from DockerSystemProfileSpawner import DockerSystemProfileSpawner as DSPS, Templates
c.JupyterHub.spawner_class = DSPS  ## this is our custom spawner. Don't change.

## The jupyter python environment MUST be set.
jupyter_venv = "/opt/jupyterhub/jupyterhub-pharma253/venv_jupyter_metrics/"
server_type = "https"   ## or "local", "proxy", "https"

c.Authenticator.admin_users = ['memo']

## Users can read/write to their home directories, but here we set other locations
## which all users can access in their volumes which are read only.
c.JupyterHub.spawner_class.volumes_ro = [
    "/opt/shared_micromamba/"     ## shared conda envs
    ##"/media/daten/"                ## share whole directory
    ##"/media/daten/software/",    ## or share specific ones
    ##"/media/daten/genomes/"
]

c.JupyterHub.spawner_class.resource_profiles = {
    ## These are maximum LIMITs to which a Docker Image can run.
    ## - At the same time, you can PREALLOCATE resources, see the preallocate
    ##   subentry in the user_profiles
    "Tiny"   : {"cpu_limit": 1,  "mem_limit": 2},
    "Small"  : {"cpu_limit": 2,  "mem_limit": 4},
    "Normal" : {"cpu_limit": 5,  "mem_limit": 10},
    "Large"  : {"cpu_limit": 10, "mem_limit": 40},
    "Extreme": {"cpu_limit": 36, "mem_limit": 80}
}

c.JupyterHub.spawner_class.docker_profiles = {
    ## These correspond quay.io images, but see
    ## https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-base-notebook
    ## for more
    ##
    ## Basic, users rely on their conda installations for software
    "SingleUser" : "quay.io/jupyterhub/singleuser:main",
    "BaseNotebook" : "quay.io/jupyter/base-notebook",
    ## Includes R, Python, and Julia at the system level, as well as their conda installations.
    ## "DataScience" : "quay.io/jupyter/datascience-notebook:latest",
    ## Add Custom
    "bash-python-r" : "docker.io/library/bash-python-r" ## This needs to be BUILT first. See README.
    ##
    ## To prevent users complaining of the slow startup times, download the required image first,
    ## and then run Jupyter.
    ## e.g. sudo docker run <URL>
}

c.JupyterHub.spawner_class.user_profiles = {
    ## Docker profiles permitted per user.
    ##
    ## The "default" entry MUST exist. These are the docker profiles
    ## permitted to any user who isn't explicitly listed below. The
    ## first entry in the list, is the preferred profile first offered
    ## to the user in the selection screen.
    ##
    "default" : {
        "allowed_resources": ["Normal", "Tiny", "Small", "Large", "Extreme"],
        "allowed_docker": ["bash-python-r", "SingleUser", "BaseNotebook"],
        "host_homedir_format_string" : "/media/daten/{username}",
        ## maximum guaranteed resources for default users
        ## - if the requested are smaller than the resource profile
        ##   then these are scaled down to that profile.
        "max_preallocate" : {"cpu_guarantee" : 5, "mem_guarantee": 10 }},

    ## User overrides
    "memo" : {
        "allowed_resources" : ["Normal", "Tiny", "Small"],
        "allowed_docker" : ["bash-python-r", "SingleUser"],  ## must be an array, not string or tuple
        "max_preallocate" : {"cpu_guarantee" : 2, "mem_guarantee": 4 },
        ##"host_homedir_format_string" : "/opt/jupyterhub/user_home/jupyter_users/{username}"}
        ## Note that conda only works when home directories are set...
        "host_homedir_format_string" : "/home/{username}"}
    ##
    ## Note: The allowed profile with the largest RAM and largest
    ## number of CPUs is the upper limit on what the HTML sliders will
    ## permit.
}

## Keep the servers alive when jupyterhub is stopped or restarted
## But ensure that when a user clicks "stop", they actually mean "delete"
c.JupyterHub.cleanup_servers = False
c.DockerSpawner.remove = True  ## Delete servers!

c.JupyterHub.sysmon_interval = 2

if server_type == "local":
    # Serve locally only
    c.JupyterHub.ip = '127.0.0.1'

elif server_type == "https":
    ## Serve HTTPS only from this machine
    c.JupyterHub.port = 443
    ## Change these to match your domain
    c.JupyterHub.ssl_cert = '/etc/letsencrypt/live/jupyter.arnold-lab.com/fullchain.pem'
    c.JupyterHub.ssl_key = '/etc/letsencrypt/live/jupyter.arnold-lab.com/privkey.pem'

elif server_type == "proxy":
    ## Change this to match your proxy, with HTTPS served on the proxy machine
    c.JupyterHub.bind_url = "http://127.0.0.1:1234" ## change to your proxy port
else:
    raise AssertionError("Give a valid server_type")

## If your notebooks are unable to find the server, check that
##  your "ufw status" allows the Docker subnet
c.JupyterHub.hub_ip = '172.17.0.1' ## This corresponds to the docker0 address

## All system users can login
c.Authenticator.allow_all = True

c.Spawner.default_url = '/lab'
c.DockerSpawner.debug = True

## This copies over templates and sets the API keys for metrics
Templates(c.JupyterHub, jupyter_venv)
