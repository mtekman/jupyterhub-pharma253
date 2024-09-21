# Ansible Installation

This has been tested for an HTTPS installation, but not yet for proxy.


### To Run:

 Create a file called `setup_vars.yml` containing contents:

    ## Dirs
    dir_pharma: /opt/jhub/jupterhub-pharma
    metrics_repo: git+https://github.com/mtekman/jupyterhub@sysmon
    venv_dir: /opt/jhub/venv
    public_url: jupyter.tekman.eu
    home_dir: "/home"         ## no trailing slash
    ## Proxy
    use_proxy: false
    proxy_bind_port: 58001    ## we assume jupyter and proxy bind to same port.
    proxy_remote_net: <public_proxy_ip>
    proxy_remote_user: proxy-jupyter
    proxy_remote_sshport: 59922
    proxy_remote_pubkey_loc: /etc/ssh/proxy-jupyter_key
    ## Docker
    docker_cpuquota_perc: 69000  ## 100% * num_cores, we leave 10 cores free
    docker_memhigh_gb: 1900      ## 230
    ## Users
    admin_users: ["<your-username-on-server>"]
    admin_email: "<your-email>" ## for certbot expiry warnings.


and then run:

    ansible-playbook -K playbooks/setup-jupyterhub-device.yaml

