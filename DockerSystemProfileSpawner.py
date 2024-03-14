from dockerspawner import SystemUserSpawner
from os.path import exists as pathexists, join as pathjoin
from pathlib import Path as currpath
from psutil import cpu_count, cpu_percent, virtual_memory
from secrets import token_hex
from shutil import copytree, rmtree


class Templates():
    ## We copy over anything in the "static" sub-directory into the Jupyter
    ## jupyter_venv environment.
    ##
    ## For now this is the only way to ensure our static resources are
    ## being loaded without the massive overhead of encoding them via the
    ## c.JupyterHub.template_vars variable.
    ##
    ## Otherwise we would simply append to the c.JupyterHub.template_paths
    ## and call it a day!
    def __init__(self, jconfig, jupyter_venv,
                 ## It is imperative that these names are NOT "js" "css" "images", as
                 ## they may overwrite existing Jupyterhub resources
                 copy_resources = ["our_js", "our_css", "our_images"]):

        repository_location = str(currpath().resolve())

        self.venv_static_dir = pathjoin(jupyter_venv, "share", "jupyterhub", "static")
        self.local_static_dir = pathjoin(repository_location, "static")
        self.templates_dir = pathjoin(repository_location, "templates")

        Templates.checkPath("VirtualEnv", self.venv_static_dir)
        Templates.checkPath("'static' folder", self.local_static_dir)
        Templates.checkPath("'templates' folder", self.templates_dir)

        ## Embed Images, JS, and CSS
        self.copy_resources = copy_resources
        self.CopyResources("images")
        self.CopyResources("js")
        self.CopyResources("css")

        ## Add templates path
        jconfig.template_paths = self.templates_dir

        ## Create API and metrics services
        api_token = Templates.initialiseMetricService(jconfig)
        self.replaceAPIToken(api_token)


    @staticmethod
    def checkPath(name, path):
        if not pathexists(path):
            raise AssertionError("'{name} cannot be found at: '{path}'"
                                 .format(name=name, path=path))

    @staticmethod
    def initialiseMetricService(jconf):
        api_token = token_hex(32)
        jconf.services = [{
            'name': 'metrics-service',
            'api_token': api_token
        }]
        jconf.load_roles = [{
            "name": "metrics-role",
            "scopes": ["read:users"],
            "services": [ "metrics-service" ]
        }]
        return(api_token)

    def replaceAPIToken(self, token):
        ## We populate the token only on the copy, not the original source.
        charts_js = pathjoin(self.venv_static_dir, "our_js", "charts.js")
        if not pathexists(charts_js):
            raise AssertionError("Unable to find 'charts.js' at '{path}'"
                                 .format(path=charts_js))

        token_from = "api_token : null,"
        token_to   = "api_token : '{token}',".format(token=token)

        new_content=""
        replaced_token = False
        with open(charts_js, 'r') as ch:
            for line in ch:
                if not replaced_token:
                    if token_from in line:
                        line = line.replace(token_from, token_to)
                        replaced_token = True
                new_content += line

        if replaced_token == False:
            raise AssertionError("Unable to find '{text}' in '{path}'"
                                 .format(text = token_from, path=charts_js))

        with open(charts_js, 'w') as ch:
            ch.write(new_content)


    def CopyResources(self, resource):
        ## Copy over new resources
        for resource in self.copy_resources:
            path_from = pathjoin(self.local_static_dir, resource)
            path_to = pathjoin(self.venv_static_dir, resource)

            if not pathexists(path_from):
                raise AssertionError("From path: " + path_from + " not found")

            if pathexists(path_to):
                print("Removing existing files at", path_to)
                rmtree(path_to)

            print("Copying", path_from, " -> ", path_to)
            copytree(path_from, path_to)


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
        self.image_homedir_format_string = self.host_homedir_format_string

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
                   <datalist id="cpu_values">
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

        ## Set the docker environment to set the user of the docker image the same as the
        ## main user.
        self.environment = {
            ##'JUPYTER_ENABLE_LAB': 'yes',
            'NB_USER': f'{self.user.name}',
            ##'NB_UID': int(self.user.uid),
            ##'NB_GID': int(self.user.gid),
        }
        options["environment"] = self.environment
        options["mem_limit"] = str(mem_limit) + "G"
        options["cpu_limit"] = cpu_limit
        options["mem_guarantee"] = str(mem_guarantee) + "G"
        options["cpu_guarantee"] = cpu_guarantee
        options['image'] = formdata['image'][0]

        ## host tells us where to look for "home" on the server
        ## image tells us where to set "home" in the image.
        ## - We set them to the same location, because this fixes an issue
        ##   where people cannot see their conda installs
        ## We need to fill these into the options later
        options['host_homedir_format_string'] = self.host_homedir_format_string
        options['image_homedir_format_string'] = self.image_homedir_format_string

        ## These are needed for the spawner to be aware of them
        self.mem_limit = options['mem_limit']
        self.cpu_limit = options['cpu_limit']
        self.mem_guarantee = options['mem_guarantee']
        self.cpu_guarantee = options['cpu_guarantee']
        self.image = options['image']

        return options
