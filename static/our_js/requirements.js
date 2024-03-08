
const Reqs = {
    selector : document.getElementById("dropdown_summary"),
    choice_element : null,

    toolJSONtoChoicesJSON : function(){
        // stores elements of optgroups
        let optgroup_map = {}
        let ordered_groups = [] // Final group array with values inside

        for (var o=0; o < tool_requirements.length; o++){
            let tool = tool_requirements[o]
            let optgroup = tool.parent_group

            if (optgroup === null){
                optgroup = "single"
            }

            if (!(optgroup in optgroup_map)){
                ordered_groups.push({
                    label: optgroup,
                    choices: []
                })
                // Location of optgroup
                optgroup_map[optgroup] = ordered_groups.length - 1
            }

            function labelText(prefix, val){
                if (val === null || val === undefined || typeof(val)==="string"){
                    return("")
                }
                if (Array.isArray(val)){
                    return(prefix + " " + val[0] + " - " + val[1])
                }
                return(prefix + " " + val)
            }

            let cores_text = labelText("CPU:", tool.cores)
            let mem_text = labelText("RAM:", tool.mem)
            ordered_groups[optgroup_map[optgroup]]
                .choices.push({
                    value : tool.name,
                    label : tool.name,
                    customProperties : {
                        cores : cores_text,
                        mem : mem_text
                    }
                })
        }
        return(ordered_groups)
    },

    summarizeChoiceItems : function(arr, type, prefix){
        // Return a text summary
        let rng = arr.map(x => x[type].split(prefix)[1])
            .filter(x => x!==undefined)
        if (rng.length === 0){
            return("")
        }
        let range = d3.extent(rng.map(x => x.split(" - ")).flat().map(x => parseInt(x)))
        let min_val = d3.min(range)
        if (d3.max(range) === min_val){
            return(prefix + "" + min_val)
        }
        return(prefix + "" + range[0] + " - " + range[1])
    },

    updateRequirementsText: function(change_event){
        let selection = Reqs.choice_element.getValue().map(x => x.customProperties)
        let mem_text = Reqs.summarizeChoiceItems(selection, "mem", "RAM: ")
        let cpu_text = Reqs.summarizeChoiceItems(selection, "cores", "CPU: ")

        Reqs.selector.innerHTML = `\
<span class="notify">Estimated Requirements:</span>\
<span class="spacer"></span>\
<span class="reqs">
  <span>${cpu_text}</span>\
  <span>${mem_text}</span>\
</span>`
    },

    customTemplate : function(template) {
        return {
            choice: (classNames, data) => {
                return template(`
          <div class="${classNames.item} ${classNames.itemChoice}
 ${data.disabled ? classNames.itemDisabled : classNames.itemSelectable}"
  data-select-text="${this.config.itemSelectText}" data-choice
 ${data.disabled ? 'data-choice-disabled aria-disabled="true"' : 'data-choice-selectable'}
  data-id="${data.id}" data-value="${data.value}"
 ${data.groupId > 0 ? 'role="treeitem"' : 'role="option"'}>
            <div class="myselect_item">
                <span>${data.label}</span>
                <span class="spacer"></span>
                <div class="myspecs">
                  <span>${data.customProperties.cores}</span>
                  <span>${data.customProperties.mem}</span>
                </div>
            </div>
          </div>
        `)},
            item: (classNames, data) => {
                // ignore the inbuilt classes
                return template(`
          <div class="item_selected" data-item data-id="${data.id}" data-value="${data.value}" >
            <span >${data.label}</span>
          </div>
        `)}
        }
    },

    init : function(){
        const element = document.getElementById('dropdown_menu');
        element.addEventListener('change', Reqs.updateRequirementsText, false)
        Reqs.choice_element = new Choices(element, {
            choices : Reqs.toolJSONtoChoicesJSON(),
            callbackOnCreateTemplates: Reqs.customTemplate
        })
        delete tool_requirements
    }
}
