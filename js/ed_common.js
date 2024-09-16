import { api } from "../../scripts/api.js";

function nodeFeedbackHandlerEd(event) {
	let nodes = app.graph._nodes_by_id;
	let node = nodes[event.detail.node_id];
	
	if(event.detail.widget_name == "log") {
		console.log("ED_log:" + event.detail.data);	
	}
	
	if(node) {
		if((event.detail.type == "sound") && (typeof node.playSound === 'function')) {
			node.playSound();
		}
		else if(event.detail.type == "text") {			
/* 		if (node.type == "MultiAreaConditioning") {
				for (const w of node.widgets) {
					if (event.detail.widget_name == w.name){
						const s = w.options.step / 10;
						w.value = Math.round(event.detail.data / s) * s;
						if (event.detail.widget_name =="resolutionX"){
							node.properties["width"] = w.value;
						}
						else if (event.detail.widget_name =="resolutionY"){
							node.properties["height"] = w.value;
						}
						node.setDirtyCanvas(true);
						break;
					}
				}
			} */			
			if (true) {
				for (const w of node.widgets) {
					if (event.detail.widget_name == w.name){					
						w.value = event.detail.data;
						break;
					}
				}
			}
		}				
	}				
}

api.addEventListener("ed-node-feedback", nodeFeedbackHandlerEd);