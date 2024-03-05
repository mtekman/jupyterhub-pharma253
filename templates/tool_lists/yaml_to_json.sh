#!/bin/bash

yq -r tool_destinations.yaml -o json \
 | jq '[.[] | to_entries | .[] | {name: .key, cores: .value.cores, mem: .value.mem}]' \
 > tool_reqs.json
