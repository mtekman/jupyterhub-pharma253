FROM quay.io/jupyter/r-notebook:4d70cf8da953
## We want R version 4.2 as that is what is on the system. Update the tag as neccesary.

# Add RUN statements to install packages as the $NB_USER defined in the base images.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

## We want users to be able to install their own conda kernels.
USER root
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    curl wget nano

## We need to expose mamba at the user level
## This is installed at: /opt/conda/bin/mamba
## Users 
COPY user_instructions.sh /etc/profile.d/02-user-instructions.sh

# Add a "USER root" statement followed by RUN statements to install system packages using apt-get,
# change file permissions, etc.

# If you do switch to root, always be sure to add a "USER $NB_USER" command at the end of the
# file to ensure the image runs as a unprivileged user by default.

## We want the bash kernel, and we want users to be able to install their own kernels, which requires jupyter.
USER ${NB_UID}

RUN mamba install --yes \
    'bash_kernel' \
    'jupyter' \
    'r-biocmanager' \
    'r-devtools' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

## And now we have to install the bash kernel
RUN python -m bash_kernel.install

## And tell it to use already installed R packages if user's have prior installation of R
ENV R_LIBS_USER="/home/${NB_USER}"/R