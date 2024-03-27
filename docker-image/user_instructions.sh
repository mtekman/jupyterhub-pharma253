#!/bin/bash

RST='\o033[0m'
YLW='\o033[1;33m'
PPL='\o033[1;35m'
CYN='\o033[1;36m'
GRN='\o033[1;32m'

cat << "EOF" | sed "s|%C|${CYN}|g;s|%R|${RST}|g;s|%G|${GRN}|g;s|%P|${PPL}|g;s|%Y|${YLW}|g"

  %C╔═══════%R %YWelcome to your Docker Container%R %C═══════╗%R
  %C║%R For information on how to install and packages %C║%R
  %C║%R manage packages in your conda environments,    %C║%R
  %C║%R please type: %Yhelpme%R                            %C║%R
  %C╚════════════════════════════════════════════════╝%R

EOF

function helpme {

    (case "$*" in
       "init"*)
           echo "\

We need to first initialise mamba and then load ('source') it

     %Pmamba init
     source ~/.bashrc%R

Now we can use it to list our environments
     ('%Yhelpme list my environments%R')

"
           ;;
       "list my"*)
           echo "\

To list your environments, first ensure you are initialised. Then
type:

     %Pmamba env list%R

If you have environments listed there, then you can activate them
    ('%Yhelpme activate an environment%R')

If you don't have environments listed there, then you can create a new one
    ('%Yhelpme create a new environment%R')

"
           ;;
       "create"*)
           echo "\

If you wish to create a new environment, first ensure you are
initialised. Then you can create a new environment by typing:

      %Pmamba create --name mynewenvironment%R

This creates a blank environment with the desired name. You can then
activate this environment ('%Yhelpme activate an environment%R')

"
           ;;
       "activate"*)
           echo "\

First list your environments to get the name ('%Yhelpme list my environments%R').
If for example you are offered an environment such as

      /media/daten/user/micromamba/envs/user_r

then you can activate that environment by typing:

      %Pmamba activate user_r%R

You can now search for packages to install in this environment
     ('%Yhelpme search for packages%R')

If you wish to deactivate the environment you are in, you can type:

     %Pmamba deactivate%R

"
           ;;
       "search"*)
           echo "\

If for example you want to install the R package 'DESeq2', then you
would type:

      %Pmamba search -c bioconda -c conda-forge '*deseq'%R

The '-c' commands specify the different 'channels' to search for, with
a priority that the bioconda channel is searched first, and then the
default conda-forge channel is searched last. We also use lowercase,
since all packages are lowecase.

This should eventually give you a long list of packages that have the
word 'deseq' somewhere in the name, as well as the versions of the
package to install.

     In the results list we notice that the top hit is 'bioconductor-deseq'

Name                   Version Build             Channel  Subdir
───────────────────────────────────────────────────────────────────────────────
 bioconductor-deseq     1.39.0  r40h037d062_0    bioconda linux-64
 bioconductor-deseq     1.38.0  r36h516909a_0    bioconda linux-64
 bioconductor-deseq     1.36.0  r36h516909a_1    bioconda linux-64

This means that we can download DESeq2 from the bioconda. We can then use this
information to install DESeq2 to a specific environment.

     ('%Yhelpme install conda packages%R')

If your package cannot be found in Conda, then that means you have to install
it manually

     ('%Yhelpme manually install R packages%R') or
     ('%Yhelpme manually install Python packages%R')
     "
           ;;
       "install conda"*)
           echo "\

To install a conda package that you've already searched for ('%Yhelpme search for packages%R'),
you first need to activate the environment ('%Yhelpme activate an environment%R') you want to
use, and then install it. For example, if we want the latest version of 'bioconductor-deseq',
then one would type:

      %Pmamba activate <myenvironment>%R
      %Pmamba install -c bioconda -c conda-forge bioconductor-deseq%R

If there are multiple packages you want to install into the same
environment, then you can add them to the end of the command:

      %Pmamba install -c bioconda -c conda-forge bioconductor-deseq snapatac r-tidyverse%R


The packages should then be installed into the environment and you now only need to
install kernels for Jupyter to see them.
     ('%Yhelpme install kernels%R')
"
           ;;
       "install kernels"*)
           echo "\
At this point you should have packages that you've installed into a conda environment
('%Yhelpme install conda packages%R'). Jupyter cannot see them yet, since it needs
to know where these 'kernels' are. To do so you need to decide if you will be
working in R, Python, or Bash.

   If working in R, we need to install the 'IRkernel' package:

          %Pmamba activate <yourenv>%R
          %Pmamba install -c conda-forge r-irkernel%R

      and then we need to now go into R, and use it:

          %PR%R
          %Glibrary(IRkernel)%R
          %GIRkernel::installspec(user=T, name='myenv', displayname='myenv')%R
          %Gquit()%R


   If working in Python, we can install the kernel easily:

          %Ppython -m ipykernel install --user --name 'myenv' --display-name 'myenv'%R


   If working in bash, the kernel is already installed and you just need to
   activate it in the document
          ('%Yhelpme with bash kernels%R')
"
           ;;
       "with bash"*)
           echo "\
To use a conda environment inside of a Bash notebook. Simply start the notebook
and in an empty cell type:

           %Pmamba activate <yourenv>%R

The rest of the notebook will now use that environment. You can selectively load
other environments into the same notebook by

          %Pmamba deactivate%R
          %Pmamba activate <otherenv>%R
"
           ;;
        "manually install R"*)
           echo "\
If you searched for an R package in conda ('%Yhelpme search for packages%R') and found
nothing for your package of choice, then you need to manually install it into
the environment ('%Yhelpme create an environment%R').

First, activate your environment:

        %Pmamba activate <yourenv>%R

For R packages from Bioconductor (e.g. 'DESeq2'):

        %PR%R
        %Gif (!require('BiocManager', quietly = TRUE))
            install.packages('BiocManager')
        BiocManager::install('DESeq2')%R

For R packages from Github or Gitlab (e.g. 'ComplexHeatmap')

        %PR%R
        %Gif (!require('devtools', quietly = TRUE))
            install.packages('devtools')
        devtools::install_github('jokergoo/ComplexHeatmap')%R

For normal R packages from CRAN (e.g. 'Hmisc')

        %PR%R
        %Ginstall.packages('Hmisc')%R


After the packages finish installing or building (this can take some
time), you will then need to install a kernel for it
       ('%Yhelpme install kernels%R')

"
           ;;
       "manually install Python"*)
           echo "\
If you searched for a Python package in conda ('%Yhelpme search for packages%R') and found
nothing for your package of choice, then you need to manually install it into
the environment ('%Yhelpme create an environment%R').

First, activate your environment:

        %Pmamba activate <yourenv>%R

For python packages in pip (e.g. sklearn):

        %Ppip install sklearn%R


After the packages finish installing, you will then need to install a kernel for it
        ('%Yhelpme install kernels%R')
"
           ;;
       "find my common"*)
           (
               echo "
This will produce a list of your R libraries sorted by descending frequency.
"
               if [[ -e ~/R_libraries.txt ]]; then
                   echo "It appears you have already run this command on $(stat -c'%y' ~/R_libraries.txt | cut -d. -f 1). Continuing now will overwrite the last results.
"
               fi

               read -p "Continue? (type 'YES' in capitals) " result_comm
               if [[ "$result_comm" != "YES" ]]; then
                   echo "Bailing. Did nothing."
                   exit 0
               fi

               echo "Searching..."
               cd ~
               find -type f -name "*.ipynb" -exec grep -oP -h "library\([^)]*\)" {} + | sed 's|\\"||g' | sed "s|'||g" | sort | uniq -c | sort -rnk 1 > R_libraries.txt
               cd - 2>/dev/null
               echo  "\
Finished.

You can view your commonly used packages by typing

           %Pcat ~/R_libraries.txt%R

If you wish you can try to automatically install these packages into an environment
       ('%Yhelpme install my commonly used R packages%R')
"
           )
           ;;
       "install my common"*)
           echo "This script attempts to find the conda packages for each of your
installed R packages. This script is BETA, and the output should be checked.
"
           local main=~/R_libraries.txt
           local attmpt=~/R_libraries_list
           echo "Generating potential candidates: R_libraries_attempt.txt"
           cat ${main} \
               | sed -r 's|.*\(([^)]*)\).*|\1|' \
               | tr '[:upper:]' '[:lower:]' \
               | awk '{print "bioconductor-"$0"\nr-"$0}' \
               | sort > ${attmpt}
           echo "Backing up candidate list"
           cp -v ${attmpt} ${attmpt}.bak;
           echo "Attempting to install candidates"
           mamba create -n blanktest --dry-run -c bioconda -c conda-forge \
                      $(cat ${attmpt}) 2>&1 \
               | grep -oP "[^ ]+(?= does not exist)" >> ${attmpt}.failed
           echo "Filtering out unknown packages"
           cat ${attmpt}.failed ${attmpt} \
               | sort | uniq -u > ${attmpt}.found
           echo "Found $(wc -l < ${attmpt}.found) packages to install."
           echo "
Please check the output of '${attmpt}.found' before continuing. There should be
no packages with duplicate names. If so, manually remove them.

Next steps:"
           echo "Please activate an environment
        ('%Yhelpme activate an environment'%R')
and then install the packages via:
          %Pmamba install -c bioconda -c conda-forge \$(cat ${attmpt}.found)%R
you will then need to install a kernel for your environment
        ('%Yhelpme install kernels'%R')

"
           ;;
       *)
           echo "\
A help info tool for %Gconda%R environments

  usage: %Yhelpme%R %Ginitialise
                list my environments
                activate an environment
                create a new environment
                search for packages
                install conda packages
                install kernels
                with bash kernels
                find my commonly used R packages
                install my commonly used R packages
                manually install R packages
                manually install Python packages
%R
                 "
        ;;
     esac) | sed "s|%C|${CYN}|g;s|%R|${RST}|g;s|%G|${GRN}|g;s|%P|${PPL}|g;s|%Y|${YLW}|g"
}