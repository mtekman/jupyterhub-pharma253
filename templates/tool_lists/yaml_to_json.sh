#!/bin/bash

tool1=1_yamlsources/tool_destinations.yaml
tool2=1_yamlsources/tool_destinations2.yaml
tool3=1_yamlsources/tools.yml

tool1json=2_processing/$(basename $tool1 .yaml).json
tool2json=2_processing/$(basename $tool2 .yaml).json
tool3json=2_processing/$(basename $tool3 .yaml).json

allcat=final/all_reqs.json
ddpcat=final/all_reqs_dedup.json
gdpcat=final/all_reqs_dedup_noempty.json
forweb=final/all_reqs_dedup_noempty_load.json

function numentries {
    local inyaml="$1"
    local message="$2"
    local outjson="$3"
    echo -e "$message$inyaml yields:\t"$(jq -s '. | length' < $outjson)
}

yq '.[] | to_entries | .[] | {name: .key, cores: .value.cores, mem: .value.mem}' \
   < ${tool1} > ${tool1json}
numentries ${tool1} "" ${tool1json}

yq '. | to_entries | .[] | {name: .key, cores: .value.cores, mem: .value.mem}' \
 < ${tool2} > ${tool2json}
numentries ${tool2} "" ${tool2json}

yq '.tools | to_entries | .[] | {name: .key, cores: .value.cores, mem: .value.mem}' \
 < ${tool3} > ${tool3json}
numentries ${tool3} "" ${tool3json}

cat ${tool1json} ${tool2json} ${tool3json} \
    | sed 's|\.\*||g' \
    | sed -r 's|[^"]*toolshed.*/repos/[^/]*/([^/]*)/[^"]*|\1|' \
    | sed 's|interactive_tool_||' \
    > ${allcat}
numentries "" "Added together" ${allcat}

jq -s '. | unique_by({name,cores,mem}) | sort_by(.name) | .[] ' < ${allcat} > ${ddpcat}
numentries "" "Deduplicated by name cores and mem" ${ddpcat}

jq -s '.[] | select(((.mem == null) and (.cores == null)) | not)' \
   < ${ddpcat} > ${gdpcat}
numentries "" "Removed entries where both cores and mem are null" ${gdpcat}

## We create a loadable JS object from this that we can source
jq -s '.' < ${gdpcat} | sed '1s|^|tool_requirements = |' > ${forweb}