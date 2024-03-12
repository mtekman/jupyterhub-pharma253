c = get_config()  #noqa

from os.path import exists as pathexists, join as pathjoin
from sys import path as modulepath

# MUST be set
repository_location = "/home/memo/repos/_mtekman/jupyterhub-pharma253/";
jupyter_venv = "/home/memo/repos/_mtekman/jupyterhub-pharma253/venv_mtekman/"

resource_profiles = {
    ## These are maximum LIMITs to which a Docker Image can run.
    ## - At the same time, you can PREALLOCATE resources, see the preallocate
    ##   subentry in the user_profiles
    "Tiny"   : {"cpu_limit": 1,  "mem_limit": 2},
    "Small"  : {"cpu_limit": 2,  "mem_limit": 4},
    "Normal" : {"cpu_limit": 5,  "mem_limit": 10},
    "Large"  : {"cpu_limit": 10, "mem_limit": 40},
    "Extreme": {"cpu_limit": 36, "mem_limit": 80}
}

docker_profiles = {
    ## These correspond quay.io images, but see
    ## https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-base-notebook
    ## for more
    ##
    ## Basic, users rely on their conda installations for software
    "SingleUser" : "quay.io/jupyterhub/singleuser:main",
    ## Includes R, Python, and Julia at the system level, as well as their conda installations.
    "DataScience" : "quay.io/jupyter/datascience-notebook:latest"
    ## Add others
    ##
    ## To prevent users complaining of the slow startup times, download the required image first,
    ## and then run Jupyter.
    ## e.g. sudo docker run <URL>
}

user_profiles = {
    ## Docker profiles permitted per user.
    ##
    ## The "default" entry MUST exist. These are the docker profiles
    ## permitted to any user who isn't explicitly listed below. The
    ## first entry in the list, is the preferred profile first offered
    ## to the user in the selection screen.
    ##
    ## Use
    "default" : {
        "allowed_resources": ["Normal", "Tiny", "Small", "Large", "Extreme"],
        "allowed_docker": ["SingleUser", "DataScience"],
        "host_homedir_format_string" : "/media/daten/{username}",
        ## maximum guaranteed resources for default users
        ## - if the requested are smaller than the resource profile
        ##   then these are scaled down to that profile.
        "max_preallocate" : {"cpu_guarantee" : 5, "mem_guarantee": 10 }},
    ## User overrides
    "memo" : { "allowed_resources" : ["Normal", "Tiny", "Small"],
               ##"allowed_docker" : ["SingleUser"],  ## must be an array, not string or tuple
               "max_preallocate" : {"cpu_guarantee" : 2, "mem_guarantee": 4 },
              ##"host_homedir_format_string" : "/opt/jupyterhub/user_home/jupyter_users/{username}"}
              ## Note that conda only works when home directories are set...
              "host_homedir_format_string" : "/home/{username}"}
    ##
    ## Note: The allowed profile with the largest RAM and largest
    ## number of CPUs is the upper limit on what the HTML sliders will
    ## permit.
}


from DockerSystemProfileSpawner import DockerSystemProfileSpawner, Templates

## Copy over all templates and initialise the API keys
Templates(c.JupyterHub, repository_location, jupyter_venv)

c.JupyterHub.spawner_class = DockerSystemProfileSpawner
c.JupyterHub.spawner_class.resource_profiles = resource_profiles
c.JupyterHub.spawner_class.docker_profiles = docker_profiles
c.JupyterHub.spawner_class.user_profiles = user_profiles

c.JupyterHub.cleanup_servers = False
c.JupyterHub.sysmon_interval = 2


## To run locally only, uncomment (1)
##(1)#c.JupyterHub.ip = '127.0.0.1'

## To serve securely with current machine as host only, uncomment(2)
##(2)#c.JupyterHub.port = 443
##(2)#c.JupyterHub.ssl_cert = '/etc/letsencrypt/live/jupyter.arnold-lab.com/fullchain.pem'
##(2)#c.JupyterHub.ssl_key = '/etc/letsencrypt/live/jupyter.arnold-lab.com/privkey.pem'

## To serve securely with currentt machine as host but with another machine as proxy, uncomment(3)
##(3)#c.JupyterHub.bind_url = "http://127.0.0.1:1234" ## change to your proxy port

## If your notebooks are unable to find the server, check that your "ufw status" allows
## the Docker subnet
c.JupyterHub.hub_ip = '172.17.0.1' ## This corresponds to the docker0 address

c.Spawner.default_url = '/lab'
c.Authenticator.admin_users = ['memo']
c.DockerSpawner.debug = True

## DEBUG:
## sudo docker stop jupyter-memo; sudo docker container rm jupyter-memo; sudo jupyterhub
