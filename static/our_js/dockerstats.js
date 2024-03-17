
import { Timers } from "./timers.js";

export const DockerStats = {

    api_token : null, // this gets replaced when jupyter starts

    Selector : {
        div_collapse : document.getElementById("collapse_docker"),
        pre_stats : document.getElementById("docker_stats"),
        span_timer : document.getElementById("docker_timer")
    },

    getMetrics : async function(){
        const data = await fetch("/hub/api/dockerstats", {
            method: 'GET',
            headers: {
                'Authorization': `token ${DockerStats.api_token}`
            }
        })
        return(data.json())
    },

    updateText : async function(){
        let metrics = await DockerStats.getMetrics()
        DockerStats.Selector.pre_stats.innerText = metrics["content"]
        DockerStats.Selector.span_timer.innerText = metrics["time"]["next_update"]
    },

    init : function(){
        const fetchevery = 5000

        new Timers("docker", DockerStats.updateText, fetchevery)
        // Collapsible div
        DockerStats.Selector.div_collapse.addEventListener("click", function(){
            let content = this.nextElementSibling;
            this.classList.toggle("active")
            if (content.style.display === "block") {
                content.style.display = "none"
                Timers.setAll("pause", false, ["docker"])
            } else {
                content.style.display = "block"
                Timers.setAll("resume", true, ["docker"])
            }
        })
    }
}