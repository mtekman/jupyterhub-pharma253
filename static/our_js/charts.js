
const Charts = {

    Metrics : {

        choice_element : null,

        // Needs to be a map of User values, with entries updated with timestamps
        //
        // e.g.1  {"User1" : [{ "time": 123455, "cpu_percent" : 1.3 }, ... ]
        // e.g.2  Map.get("User1").push({ new_vals })
        timescale_data : new Map(),   // new data coming in
        hist_data : new Map(),        // summarized data from timescale_data

        generateFakeMetrics: function(){
            "Class purely for debugging. It fakes the metrics that would be output from fetchData()"
            const rand_frac = 1.5 + (Math.random() * 1.5)
            const total_cpu_all = Math.random() * 100
            const total_cpu_jpy = (total_cpu_all / rand_frac)  + (Math.random() * total_cpu_all / rand_frac);
            const total_mem_all = Math.random() * 5000
            const total_mem_jpy = (total_mem_all / rand_frac)  + (Math.random() * total_mem_all/ rand_frac);

            var metr = {
                "time" : {
                    "cached": Date(), "now" : Date.now(), "update_interval" : 2,
                    "next_update" : 2, "last_update" : 8.6
                },
                "system" : {
                    "ram_free_gb" : 119,  "ram_used_gb" : 2.8, "ram_total_gb" : 202.3,
                    "ram_usage_percent" : 2.3, "cpu_usage_percent" : 2.1, "cpu_count" : 36
                },
                "user" : {
                    "cpu_percent" : {
                        "all_processes": total_cpu_all, "all_jupyter_users": total_cpu_jpy
                    },
                    "memory_rss_mb": {
                        "all_jupyter_users": total_mem_jpy, "all_processes": total_mem_all
                    }
                }
            }
            var remaining_mem = total_mem_jpy
            var remaining_cpu = total_cpu_jpy

            var user_count = 0
            while ((remaining_mem > 0) && (remaining_cpu > 0))
                {
                    let username = "user" + user_count

                    metr["user"]["cpu_percent"][username] = 1 + Math.random() * remaining_cpu
                    metr["user"]["memory_rss_mb"][username] = 1 + Math.random() * remaining_mem

                    remaining_cpu -= metr["user"]["cpu_percent"][username]
                    remaining_mem -= metr["user"]["memory_rss_mb"][username]

                    user_count += 1
                }
            return(metr)
        },

        init : function(){
            Charts.Metrics.hist_data.set("all_processes", [])
            Charts.Metrics.initializeUserSelectBox()
        },

        populateTimeScale: function(){
            // Data are the metrics
            const metrics = Charts.Metrics.generateFakeMetrics()
            const time = metrics.time.now

            for (username in metrics.user.cpu_percent){
                const packet = { "time" : time,
                    "cpu_percent" : metrics.user.cpu_percent[username],
                    "memory_rss_mb" : metrics.user.memory_rss_mb[username]}

                if (Charts.Metrics.timescale_data.has(username)){
                    Charts.Metrics.timescale_data.get(username).push(packet)
                } else {
                    Charts.Metrics.timescale_data.set(username, [packet])
                    // Add unique colouring
                    let user_color = Charts.Style.getRandomColor()
                    if (!(Charts.Style.style_map.has(username))){
                        Charts.Style.style_map.set(username, { "color" : user_color,
                            "width" : 2 })
                        Charts.Metrics.choice_element.setChoices(
                            [{"label" : username,
                                "value" : username,
                                "selected": false,
                                "customProperties": {
                                    "color": user_color
                                }
                            }], "value", "label",
                            false) // false means that we dont replace the existing choices.
                    }
                }
            }
        },

        initializeUserSelectBox: function(){
            Charts.Metrics.choice_element = new Choices(Charts.Selector.user_active, {
                callbackOnCreateTemplates: Charts.Metrics.customTemplate
            })
            // Set default choices
            for (var user of [["all_processes", "System"], ["all_jupyter_users", "JupyterUsers"]]){
                Charts.Metrics.choice_element.setChoices(
                    [{"label" : user[1], "value" : user[0], "selected": true,
                        "customProperties": {"color": Charts.Style.style_map.get(user[0]).color}
                    }],
                    "value", "label", false)
            }
        },

        customTemplate : function(template) {
            return {
                choice: (classNames, data) => {
                    return template(`
          <div class="myselect_item ${classNames.item} ${classNames.itemChoice}
 ${data.disabled ? classNames.itemDisabled : classNames.itemSelectable}" data-choice
 ${data.disabled ? 'data-choice-disabled aria-disabled="true"' : 'data-choice-selectable'}
  data-id="${data.id}" data-value="${data.value}"
 ${data.groupId > 0 ? 'role="treeitem"' : 'role="option"'}>
                <span style="background-color: ${data.customProperties.color}" >
                  &nbsp;
                </span>
                <span>&nbsp;${data.label}</span>
          </div>
        `)},
                item: (classNames, data) => {
                    // ignore the inbuilt classes
                    return template(`
          <div class="item_selected" data-item data-id="${data.id}" data-value="${data.value}" >
            <span style="background-color: ${data.customProperties.color}">&nbsp;</span>
            <span style="color:${data.customProperties.color};">${data.label}</span>
          </div>
        `);
                }
            }}
    },

    Selector : {
        user_highlight : document.getElementById("highlighted_user"),
        user_active : document.getElementById("active_users")
    },

    Style : {

        stroke_width_user : 2,
        stroke_width_user_highlight : 6,
        style_map : new Map(),

        init : function(){
            Charts.Style.style_map.set("all_processes", {"color" : '#e41a1c', "width" : 5 })
            Charts.Style.style_map.set("all_jupyter_users", {"color" : '#377eb8', "width" : 4})
        },

        getRandomColor : function(){
            var letters = '0123456789ABCDEF'
            var color = '#';
            for (var i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        },

        generateNewStyleMap: function(show_user_list){
            // Create a new style map which greys out unwanted users
            const new_style_map = new Map(Charts.Style.style_map)
            for (const [user, opts] of new_style_map) {
                if (show_user_list.indexOf(user)===-1){
                    // If not in show list, grey it out
                    new_style_map.set(user, { "color" : "#aaaaaa", "width" : 0.5 })
                }
            }
            return(new_style_map)
        }
    },

    Timers : {

        _db : {}, // internal database of all timers

        get : function(name){
            return(Charts.Timers._db[name])
        },

        newTimer: function(name, do_func, millisecs) {
            var timer
            obj = {};
            obj.resume = function() {
                timer = setInterval(do_func, millisecs);
            };
            obj.pause = function() {
                clearInterval(timer);
            };
            obj.resume()
            Charts.Timers._db[name] = obj;
        }
    },

    Smooth : {
        /* Functions for processing timescale data, by squashing older
         * data into the history map, and then smoothing the history map
         * when that gets too big */
        begin_smoothing_history : false,

        squashDataOlderThan : function(last_ms = 1000){
            //Historical data gets merged into a single average, every n ticks

            let ref_array = Charts.Metrics.timescale_data.get("all_processes")
            var min_time = Date.now() - last_ms
            //if (ref_array.filter(x => x.time < min_time).length > 20){

            for (const [user, arrays] of Charts.Metrics.timescale_data)
                {
                    let data_before = arrays.filter(x => x.time < min_time)
                    let len_data = data_before.length
                    let data_summed = data_before
                        .reduce((acc, obj) => {
                            acc.cpu_percent += obj.cpu_percent || 0;
                            acc.memory_rss_mb += obj.memory_rss_mb || 0;
                            return acc;
                        }, {cpu_percent: 0, memory_rss_mb: 0})

                    let data_avg = {
                        "time" : min_time,
                        "cpu_percent" : (data_summed.cpu_percent / len_data) || 0,
                        "memory_rss_mb" : (data_summed.memory_rss_mb / len_data) || 0
                    }

                    if (Charts.Metrics.hist_data.has(user)){
                        Charts.Metrics.hist_data.get(user).push(data_avg)
                    } else {
                        Charts.Metrics.hist_data.set(user, [data_avg])
                    }

                    // Shorten all histories, but use last value of hist as starting point
                    Charts.Metrics.timescale_data.set(user, [data_avg].concat(arrays.filter(x => x.time >= min_time)))
                    //Charts.Metrics.timescale_data.set(user, arrays.filter(x => x.time >= min_time))
                }
        },

        smoothHistory : function(hist_limit = 25){
            let ref_hist = Charts.Metrics.hist_data.get("all_processes")
            if (ref_hist.length > hist_limit){
                for (const [user, arrays] of Charts.Metrics.hist_data)
                    {
                        var new_arr = []
                        for (let i=1; i < arrays.length; i += 2){
                            let valA = arrays[i-1]
                            let valB = arrays[i]

                            new_arr.push({
                                "time": (valA.time + valB.time) / 2,
                                "cpu_percent" : (valA.cpu_percent + valB.cpu_percent) / 2,
                                "memory_rss_mb" : (valA.memory_rss_mb + valB.memory_rss_mb) / 2
                            })
                            //new_arr.push(valB)
                        }
                        // Set time for first and last to match limits of original, for continuity
                        new_arr[0].time = arrays[0].time
                        new_arr[new_arr.length-1] = arrays[arrays.length-1]
                        Charts.Metrics.hist_data.set(user, new_arr)
                    }
            }
        },

        headTimescale: function(how_many_to_plot){
            // Head the timescale_data, and prepend the last hist_data
            var filtered_data = new Map()
            for (var [user, arrays] of Charts.Metrics.timescale_data)
                {
                    var last_hist = []
                    if (Charts.Metrics.hist_data.has(user)){
                        last_hist = Charts.Metrics.hist_data.get(user).slice(-1) || []
                    }
                    filtered_data.set(user, last_hist.concat(arrays.slice(-how_many_to_plot)))
                }
            return(filtered_data)
        }
    },

    Plot : class Plot {

        size_of_letter = 15

        constructor(name, margin, width, height,
            ytype="cpu_percent", show_xticks=true){
                this.name = name
                this.width = width
                this.height = height
                this.ytype = ytype
                this.show_xticks = show_xticks
                this.svg = d3.select("#" + name) //"#my_dataviz")
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", `translate(${margin.left},${margin.top})`);
                this.initAxes(width, height)
            }

        initAxes(width, height){
            // Initialize axes if not present
            let xnew_dom = document.getElementById(this.name + "_xaxis-new"),
                  xold_dom = document.getElementById(this.name + "_xaxis-old"),
                  yaxis_dom = document.getElementById(this.name + "_yaxis")

            if (xnew_dom != null){
                xnew_dom.remove()
                xold_dom.remove()
                yaxis_dom.remove()
            }

            // xold
            this.svg.append("g").attr("id", this.name + "_xaxis-old")
                .attr("class", "xaxis")
                .attr("transform", `translate(0, ${height})`)

            // xnew
            this.svg.append("g").attr("id", this.name + "_xaxis-new")
                .attr("class", "xaxis")
                .attr("transform", `translate(0, ${height})`)
            // y
            this.svg.append("g").attr("id", this.name + "_yaxis")
        }

        updateAxes(hist_width, xold, xnew, y){
            // Update the axis ranges
            let len_hist_items = Math.floor(hist_width / (1.5 * this.size_of_letter))
            let len_ref_items = 2

            // xold
            if (this.show_xticks){
                this.svg.select("#" + this.name + "_xaxis-old")
                    .call(d3.axisBottom(xold).ticks(len_hist_items).tickFormat(Charts.Plot.formatDate))
                // xnew
                this.svg.select("#" + this.name + "_xaxis-new")
                    .call(d3.axisBottom(xnew).ticks(len_ref_items).tickFormat(Charts.Plot.formatDate))
            }
            // y
            this.svg.select("#" + this.name + "_yaxis").call(d3.axisLeft(y).ticks(5))
        }

        calculateAxes(historical_ref, incoming_ref, hist_width){
            // Update the axis ranges
            const xold = d3.scaleLinear().domain(d3.extent(historical_ref, d => d.time))
                .range([ 0, hist_width])

            const xnew = d3.scaleLinear()
                .domain(d3.extent(incoming_ref, d => d.time))
                .range([ hist_width, this.width ])

            let y;
            if (this.ytype === "cpu_percent"){
                //y = d3.scaleLinear().domain([0, 100]).range([ this.height, 0 ]);
                y = d3.scaleLinear()
                    .domain([0, d3.max(
                        historical_ref.concat(incoming_ref),
                        d => d[this.ytype])])
                    .range([ this.height, 0 ]);
            } else {
                // Assume RAM
                y = d3.scaleLinear()
                    .domain([0, d3.max(
                        historical_ref.concat(incoming_ref),
                        d => d.memory_rss_mb)])
                    .range([ this.height, 0 ]);
            }

            return([xold,xnew,y])
        }

        static calculateDpoints(d, x, y, ykey="cpu_percent", docurve=false){
            let crv = d3.line()
                .x(d => x(d.time))
                .y(d => y(d[ykey]))

            if (docurve){
                crv = crv.curve(d3.curveBasis)
            }
            return(crv(d[1]))
        }

        static formatDate(d){
            let now = new Date(d)
            let hours = String(now.getHours()).padStart(2, '0');
            let minutes = String(now.getMinutes()).padStart(2, '0');
            let seconds = String(now.getSeconds()).padStart(2, '0');
            //return(`${hours}:${minutes}:${seconds}`);
            return(`${minutes}:${seconds}`);
        }

        plotDataTo(classname, new_style_map, x, y,
            trans_time, data, docurve=false){
                // Plot the current data
                let lines = this.svg.selectAll("path." + classname)
                lines = lines
                    .data(data, function(grp_arr, ind, whole){
                        return(ind)
                    })
                    .join(enter => enter
                        .append("path")
                        .attr("class", classname)
                        .attr("fill", "none")
                        .attr("stroke", d => new_style_map.get(d[0]).color )
                        .attr("stroke-width", d => new_style_map.get(d[0]).width)
                        .attr("d", d => Charts.Plot.calculateDpoints(d, x, y,
                            this.ytype, docurve))
                        .on("mouseover", function(ev){
                            let path = ev.target
                            let pathname = path.__data__[0]
                            Charts.Selector.user_highlight.innerText = pathname
                            path.style.strokeWidth = Charts.Style.stroke_width_user_highlight
                            Charts.Timers.get("render").pause()
                        })
                        .on("mouseout", function(ev){
                            let path = ev.target
                            let pathname = path.__data__[0]
                            path.style.strokeWidth = new_style_map.get(pathname).width
                            Charts.Selector.user_highlight.innerText = null
                            Charts.Timers.get("render").resume()
                        }),
                        update => update,
                        function(exit){
                            //console.log("exit", exit)
                            return(exit.call(lines => lines.remove().attr("d" ,"") ))
                        })
                    .call(lines => lines.transition().duration(trans_time)
                        .attr("fill", "none")
                        .attr("stroke", d => new_style_map.get(d[0]).color )
                        .attr("stroke-width", d => new_style_map.get(d[0]).width)
                        .attr("d", d => Charts.Plot.calculateDpoints(d, x, y,
                            this.ytype, docurve)))
            }

        render(trans_time_new, trans_time_hist)
            {
                const ref_hist = Charts.Metrics.hist_data.get("all_processes")
                const hist_width_limit = 0.8 * this.width
                // We smooth the history data if it's taking up 80% of the screen
                // but we let it build up across the screen first before smoothing.
                var hist_width = ref_hist.length * this.size_of_letter;  // build up
                if (Charts.Smooth.begin_smoothing_history || (hist_width > hist_width_limit))
                    {
                        Charts.Smooth.begin_smoothing_history = true
                        hist_width = hist_width_limit   // hold fixed once smoothing starts

                        let approx_items = Math.floor(hist_width_limit / this.size_of_letter)
                        Charts.Smooth.smoothHistory(approx_items)
                    }

                // Free space divided by letter spacing
                var how_many_to_plot = Math.floor((this.width - hist_width) / this.size_of_letter)
                const filtered_data = Charts.Smooth.headTimescale(how_many_to_plot)
                const ref_filt = filtered_data.get("all_processes")

                const [xold, xnew, y] = this.calculateAxes(ref_hist, ref_filt, hist_width)
                this.updateAxes(hist_width, xold, xnew, y)

                var new_style_map = Charts.Style.generateNewStyleMap(
                    Charts.Metrics.choice_element.getValue().map(x => x.value)
                )

                this.plotDataTo("old", new_style_map, xold, y, trans_time_hist,
                    Charts.Metrics.hist_data, true)
                this.plotDataTo("new", new_style_map, xnew, y, trans_time_new,
                    filtered_data, false)
            }
    },

    init : function(){
        Charts.Style.init()
        Charts.Metrics.init()

        const squash_every = 1000
        const trans_time_new = 150
        const trans_time_hist = 0
        const plot_every = 500
        const fetch_every = 500

        Charts.Timers.newTimer("populate", Charts.Metrics.populateTimeScale,
            fetch_every)
        Charts.Timers.newTimer("squash", function(){
            Charts.Smooth.squashDataOlderThan(squash_every)
        }, squash_every)

        Charts.Metrics.populateTimeScale()

        const margin = {top: 5, right: 30, bottom: 40, left: 60}
        const width = 460 - margin.left - margin.right
        const height = 200 - margin.top - margin.bottom

        // CPU plot
        var p1 = new Charts.Plot("cpu", margin, width, height, "cpu_percent", show_xticks=false)
        // RAM plot
        var p2 = new Charts.Plot("ram", margin, width, height, "memory_rss_mb")
        // They share a common Timer
        Charts.Timers.newTimer("render", function(){
            p1.render(trans_time_new, trans_time_hist)
            p2.render(trans_time_new, trans_time_hist)
        }, plot_every)
    }
}
