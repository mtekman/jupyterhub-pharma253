import "/hub/static/our_js/libraries/choices.min.js";
import { Reqs } from "/hub/static/our_js/requirements.js";
fetch("/hub/static/our_js/tool_list.json")
  .then(response => response.json())
  .then(json => {
      Reqs.init(json)
  })
