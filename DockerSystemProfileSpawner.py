# [[file:../../../../../mnt/galaxy_data/repos/_mtekman/org-projects/brain/20240226120319-jupyterhub_docker.org::*Module][Module:1]]
from os.path import sep as fsep
from dockerspawner import SystemUserSpawner
from psutil import virtual_memory, cpu_percent, cpu_count

class DockerSystemProfileSpawner(SystemUserSpawner):

    _SEP_="|" ## class delimiter used
    
    @staticmethod
    def datalistOptions(valranges):
        """For a list of integers, convert into datalist entries"""
        return(" ".join(
            ["<option value='{x}'></option>".format(x=x) for x in valranges]))

    ## @staticmethod
    ## def getCurrentSystemResources():
    ##     free_mem = round(virtual_memory()._asdict()["available"] / 1e9)
    ##     free_cpu = round(100 * (1- cpu_percent()))
    ##     return([free_mem, free_cpu])
    
    def ResourceSelect(self):
        """This function generates the HTML select options needed to
        present the CPU and RAM profiles in the webpage for the user
        """
        select_text = "<select id='profile' "
        ## Inline JS for updating the sliders on selection
        select_text += "onchange=\"res = this.value.split('" + self._SEP_ + "');"
        select_text += "document.getElementById('cpus_slider').value = res[0];"
        select_text += "document.getElementById('cpu_limit').value = res[0];"
        select_text += "document.getElementById('memg_slider').value = res[1];"
        select_text += "document.getElementById('mem_limit').value = res[1];"
        select_text += "document.getElementById('nam_val').value = res[2];"
        select_text += "\" >"

        ## Decide which usage profiles the user can run
        allowed_resources =  self.getUserProfileSubEntry("allowed_resources")
        selected_profile = allowed_resources[0]
        sorted_allowed_resources, _ = zip(*sorted(zip(allowed_resources, self.resource_profiles.keys()), reverse=True))

        tick_cpus=[]
        tick_mems=[]
        for prof in sorted_allowed_resources:
            cpu_limit = self.resource_profiles[prof]["cpu_limit"]
            mem_limit = self.resource_profiles[prof]["mem_limit"]
            option_text = "\n<option value='{cpu}{sep}{mem}{sep}{nam}' {selected} >{nam}</option>".format(
                    cpu=str(cpu_limit), mem=str(mem_limit), nam=prof, sep=self._SEP_,
                    selected="selected" if (prof == selected_profile) else ""
            )
            tick_cpus.append(cpu_limit)
            tick_mems.append(mem_limit)
            select_text += option_text        
        select_text +="\n</select>"    
        return([select_text, tick_cpus, tick_mems])

    def DockerImageSelect(self):
        """This function generates the HTML select options needed to
          present docker images in the webpage to the user
        """
        ## Decide which images the user can run
        allowed_docker = self.getUserProfileSubEntry("allowed_docker")
        selected_image = allowed_docker[0]
        sorted_allowed_docker, _ = zip(*sorted(zip(allowed_docker, self.docker_profiles.keys()), reverse=True))

        ## We also need to tell Jupyter which URLs are allowed
        self.allowed_images = [self.docker_profiles[img] for img in allowed_docker]

        select_text = "<select name='image' id='image'>"
        select_text += "\n".join([
            "<option value='{image_url}' {selected} >{image_name}</option>".format(
                image_url=self.docker_profiles[prof], image_name=prof,
                selected="selected" if (prof == selected_image) else ""
        ) for prof in sorted_allowed_docker])
        select_text += "\n</select>"
        return(select_text)

    def getUserProfileSubEntry(self, subentry):
        username = self.user.name
        if (username not in self.user_profiles) or (subentry not in self.user_profiles[username]):
            username = "default"
            if subentry not in self.user_profiles[username]:
                raise AssertionError("You have not defined '{subentry}' in your \"default\" user_profiles".format(subentry=subentry))
        return(self.user_profiles[username][subentry])

        
    def _options_form_default(self):
        default_cpus=4
        default_memg=5
        profile_select, tick_cpu, tick_mem = self.ResourceSelect()
        image_select = self.DockerImageSelect()
        max_preallocate = self.getUserProfileSubEntry("max_preallocate")

        ## Store the max mem and cpu values for the user, so that we
        ## can validate these later, just in case they try to inject
        ## values with a permissive browser.
        self.max_mem = max(tick_mem)
        self.max_cpu = max(tick_cpu)

        self.host_homedir_format_string = self.getUserProfileSubEntry("host_homedir_format_string")

        return """
        <div id="profile_cont">
          <label for="profile">Usage:</label>
          {profile_select}
          <span></span>
          <label for="image">Image:</label>
          {image_select}
          <input id="nam_val" name="nam_val" type="text" hidden="true" />
        </div>
        <div id="usage_cont">
        <table>
        <thead><th>How many CPUs?</th><th>How much MEM?</th></thead>
        <tr><td>
                <div class="slider">
                   <input id="cpus_slider" value="{cpus}" type="range"
                     list="cpu_values" min="1" max="{max_cpu}"
                     oninput="cpu_limit.value = this.value" />
                   <datalist id="cpu_values"
                     {cpu_tick_values}
                   </datalist>
                </div>
            </td>
            <td>
                <div class="slider">
                    <input id="memg_slider" value="{memg}" type="range" 
                     list="mem_values" min="2" max="{max_mem}"
                     oninput="mem_limit.value = this.value" />
                    <datalist id="mem_values" >
                     {mem_tick_values}
                    </datalist>
                </div>
            </td>                 
        </tr>
        <tr>
          <td><input id="cpu_limit" name="cpu_limit" value="{cpus}" type="number" 
                list="cpu_values" min="1" max="{max_cpu}"
                oninput="cpus_slider.value = this.value" />
                <label for="cpu_limit"> cores</label>
          </td>
          <td><input id="mem_limit" name="mem_limit" value="{memg}" type="number"
                list="mem_values" min="2" max="{max_mem}"
                oninput="memg_slider.value = this.value" />
                <label for="mem_limit"> GB</label>
           </td>
        </tr>
        </table>
        </div>
        <span id="prealloc_message"><b>Note:</b>Only up to {prealloc_max_cpu} cores and {prealloc_max_mem}GB can be pre-allocated.</span>
        """.format(cpu_tick_values=self.datalistOptions(tick_cpu),
                   mem_tick_values=self.datalistOptions(tick_mem),
                   profile_select=profile_select,
                   image_select=image_select,
                   prealloc_max_cpu=max_preallocate["cpu_guarantee"],
                   prealloc_max_mem=max_preallocate["mem_guarantee"],
                   max_cpu=self.max_cpu,   max_mem=self.max_mem,
                   cpus=default_cpus,      memg=default_memg)

    def validateResourceLimits(self, cpu_limit, mem_limit):
        ## Scale down preallocation limits if profile doesn't need that much
        ## Validate user options with server
        if cpu_limit > self.max_cpu:
            raise AssertionError("{username} requested {N} cores, but is permitted only {M}".format(
                username=self.user.name, N=cpu_limit, M=self.max_cpu
            ))        
        if mem_limit > self.max_mem:
            raise AssertionError("{username} requested {N} GB memory, but is permitted only {M} GB".format(
                username=self.user.name, N=mem_limit, M=self.max_mem
            ))
        ##
        max_preallocate = self.getUserProfileSubEntry("max_preallocate")
        ##
        mem_guarantee = mem_limit if mem_limit <= max_preallocate["mem_guarantee"] else max_preallocate["mem_guarantee"]
        cpu_guarantee = cpu_limit if cpu_limit <= max_preallocate["cpu_guarantee"] else max_preallocate["cpu_guarantee"]

        return([cpu_limit, mem_limit, cpu_guarantee, mem_guarantee])

    
    def options_from_form(self, formdata):
        options = {}

        cpu_limit, mem_limit, cpu_guarantee, mem_guarantee = self.validateResourceLimits(
            int(formdata['cpu_limit'][0]), int(formdata['mem_limit'][0])
        )
        
        options["mem_limit"] = str(mem_limit) + "G"
        options["cpu_limit"] = cpu_limit
        options["mem_guarantee"] = str(mem_guarantee) + "G"
        options["cpu_guarantee"] = cpu_guarantee
        options['image'] = formdata['image'][0]

        ## These are needed for the spawner to be aware of them
        self.mem_limit = options['mem_limit']
        self.cpu_limit = options['cpu_limit']
        self.mem_guarantee = options['mem_guarantee']
        self.cpu_guarantee = options['cpu_guarantee']
        self.image = options['image']

        return options
# Module:1 ends here
