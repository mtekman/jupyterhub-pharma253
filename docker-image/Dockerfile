FROM quay.io/jupyter/r-notebook:4d70cf8da953
## We want R version 4.2 as that is what is on the system. Update the tag as neccesary.

# Add RUN statements to install packages as the $NB_USER defined in the base images.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

## We want users to be able to install their own conda kernels
## - we also add zstandard libraries for .conda to work?
USER root
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    curl wget nano zstd vim patch

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
    'zstandard' \
    'bash_kernel' \
    'jupyter' \
    'r-biocmanager' \
    'r-devtools' \
    'r-svglite'

## Force zstandard reinstall (due to ongoing bug..)
RUN pip install --upgrade --force-reinstall zstandard

## Update the base installation
RUN mamba update --yes -n base -c conda-forge -c bioconda --all

## Remove locks
RUN mamba clean --all -f -y
RUN fix-permissions "${CONDA_DIR}" && fix-permissions "/home/${NB_USER}"

## Install the bash kernel
RUN python -m bash_kernel.install

## And tell it to use already installed R packages if user's have prior installation of R
ENV R_LIBS_USER="/home/${NB_USER}"/R

## Finally add the right channels to the condarc, and remove the systemrc
RUN rm /opt/conda/.condarc

## Remove annoying banner
## RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

## Copy over the mamba RC containing the shared installation
COPY shared_mamba.rc  /opt/conda/.condarc

