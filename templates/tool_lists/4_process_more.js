
// Load in the tool_requirements JSON

function longestPrefix(words){
    // check border cases size 1 array and empty first word)
    if (!words[0] || words.length ==  1) return words[0] || "";
    let i = 0;
    // while all words have the same character at position i, increment i
    while(words[0][i] && words.every(w => w[i] === words[0][i]))
            i++;
    // prefix is the substring from the beginning to the last successfully checked i
    return words[0].substr(0, i);
}

// Find common groups of tools to serve as opt groups
// Add indices, and empty parent groups
tool_requirements.map((x,i) => {x.index = i})
tool_requirements.map(x => {x.parent_group = {}}) // frequency list
tool_requirements.map(x => {x.name = x.name.toLowerCase()}) // downcase all tools
var tool_map = {}  // log any duplicate groups

for (var i=0; i < tool_requirements.length; i++){

    let name = tool_requirements[i].name.toLowerCase()
    if (name in tool_map){
        tool_map[name].push(tool_requirements[i].index)
    } else {
        tool_map[name] = [tool_requirements[i].index]
    }
    // We use this seed to search forward in the sorted list of tool
    for (var s=3; s < 10; s++){
        let seed = name.substr(0,s) // try varying seeds
        // matching tools
        let matching_tools = tool_requirements.filter(x => x.name.substr(0,s) === seed)

        // A group is a group if it has at least 2 members in it (e.g. funannotate, but not IDM)
        if (matching_tools.length > 2){
            // Find longest common prefix, stripping any trailing"_"
            let common_prefix = Page.longestPrefix(matching_tools.map(x => x.name))

            if (common_prefix.substr(common_prefix.length - 1,1) === "_"){
                common_prefix = common_prefix.substr(0, common_prefix.length -1)
            }
            // If the longest is something like "picard_C" or
            // "chira_m", discard the bit after the hypen
            if (common_prefix.substr(common_prefix.length - 2,1) === "_"){
                common_prefix = common_prefix.substr(0, common_prefix.length - 2)
            }

            for (var m=0; m < matching_tools.length; m++){
                let mtool = matching_tools[m];
                let match_index = mtool.index
                // Push parent match to selection
                let count = tool_requirements[match_index].parent_group[common_prefix] || 0
                tool_requirements[match_index].parent_group[common_prefix] = count + 1
            }
        }
    }
}
// Do a second pass through each parent group, assign the most populous
for (var i=0; i < tool_requirements.length; i++){
    let groups = tool_requirements[i].parent_group
    let group_keys = Object.keys(groups)
    let group_vals = Object.keys(groups)

    if (group_keys.length > 1){
        let max_index = group_vals.indexOf(d3.max(group_vals))
        let max_group = group_keys[max_index]
        tool_requirements[i].parent_group = max_group
    } else if (group_keys.length === 1) {
        tool_requirements[i].parent_group = group_keys[0]
    } else {
        tool_requirements[i].parent_group = null
    }
}
// // Collapse requirements into groups too
let dupes = Object.entries(tool_map).filter(x => x[1].length > 1)
for (var i=0; i < dupes.length; i++){
    let dupe_indices = dupes[i][1]
    let keep_this = dupe_indices[0]
    let move_these = dupe_indices.slice(1) // everything after is merged

    // Convert requirements to arrays
    tool_requirements[keep_this].cores = [tool_requirements[keep_this].cores]
    tool_requirements[keep_this].mem = [tool_requirements[keep_this].mem]

    for (var m=0; m < move_these.length; m++){
        // Append requirements
        let entry = tool_requirements[move_these[m]]
        if (entry.cores !== null){
            tool_requirements[keep_this].cores.push(entry.cores)
        }
        if (entry.mem !== null){
            tool_requirements[keep_this].mem.push(entry.mem)
        }
        if (entry.parent_group !== null){
            if (entry.parent_group !== tool_requirements[keep_this].parent_group){
                console.error("Mismatch of parent groups", dupe_indices)
            }
        }
        // Null the entry
        tool_requirements[move_these[m]] = null
    }
    // Remove any null and flatten single entries
    tool_requirements[keep_this].cores = tool_requirements[keep_this].cores.filter(x => x!=null)
    if (tool_requirements[keep_this].cores.length === 1){
        tool_requirements[keep_this].cores = tool_requirements[keep_this].cores[0]
    }
    tool_requirements[keep_this].mem = tool_requirements[keep_this].mem.filter(x => x!=null)
    if (tool_requirements[keep_this].mem.length === 1){
        tool_requirements[keep_this].mem = tool_requirements[keep_this].mem[0]
    }
}
// Reindex the array and remove nulls
tool_requirements = tool_requirements.filter(x => x !== null)
for (var m=0; m < tool_requirements.length; m++){        
    delete tool_requirements[m].index
}

// Save the tool_requirements as tools_groups.json