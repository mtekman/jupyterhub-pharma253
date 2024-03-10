import { Reqs } from "./static/our_js/requirements.js";
fetch("./static/our_js/tool_list.json")
  .then(response => response.json())
  .then(json => {
      Reqs.init(json)
  })
