import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyDialog, $el } from "../../scripts/ui.js";
import { ComfyApp } from "../../scripts/app.js";
import { ClipspaceDialog } from "../../extensions/core/clipspace.js";

import { showMessage, findWidgetByName } from "./node_options/common/utils.js";


let wildcards_list = [];
async function load_wildcards() {
	let res = await api.fetchApi('/impact/wildcards/list');
	let data = await res.json();
	wildcards_list = data.data;
}

load_wildcards();

async function uploadImage(filepath, formData) {
    try {
        await api.fetchApi('/upload/image', {
            method: 'POST',
            body: formData
        });

        const selectedIndex = ComfyApp.clipspace['selectedIndex'];
        ComfyApp.clipspace.imgs[selectedIndex] = new Image();
        ComfyApp.clipspace.imgs[selectedIndex].src = `view?filename=${filepath.filename}&type=${filepath.type}`;

        if (ComfyApp.clipspace.images) {
            ComfyApp.clipspace.images[selectedIndex] = filepath;
        }

        ClipspaceDialog.invalidatePreview();
    } catch (error) {
        console.error('Error uploading image:', error);
    }
}

function getNodeFromLink(node, linkId) {
    const linkInfo = app.graph.links[linkId];
    return node.graph.getNodeById(linkInfo.origin_id);
}

function isMatchingNode(node, nodeType) {
    return node.type && node.type.includes(nodeType);
}

 function findPreviousNode(node, nodeType) {	
	if (!node) return null;		
    const linkId = node.inputs[2]?.link;
    if (!linkId) return null;
    const targetNode = getNodeFromLink(node, linkId);
    if (isMatchingNode(targetNode, nodeType)) {
        return targetNode;
    }
    return null;
}

function find_script_load_image(width, height, reg_script="Regional Script 💬ED", load_image="LoadImage") {
	const script_nodes = app.graph._nodes.filter( (n) => n.type.includes(reg_script));
	let find_node_list = []
	if (script_nodes.length) {
		script_nodes.forEach( (n) => {
			find_node_list.push(findPreviousNode(n, load_image));
		});
	}
	if (find_node_list.length) {
		find_node_list.forEach( (n) => {
			if (n) ComfyApp.pasteFromClipspace(n);
		});		
	}
	const eff_loader = app.graph._nodes.find((n) => n.type.includes("Efficient Loader 💬ED"));
	if (eff_loader) {
		let widget_width = findWidgetByName (eff_loader, "image_width");
		let widget_height = findWidgetByName (eff_loader, "image_height");
		widget_width.value = width;
		widget_height.value = height;
	}
}

async function createEmptyImage(width, height, color="white") {
    try {
        // Canvas 생성 및 설정
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext("2d");
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, width, height);

        // Data URL 생성
        const imageDataURL = canvas.toDataURL("image/png");

        // Blob 생성
        const byteString = atob(imageDataURL.split(',')[1]);
        const byteArray = new Uint8Array(byteString.length);
        for (let i = 0; i < byteString.length; i++) {
            byteArray[i] = byteString.charCodeAt(i);
        }
        const myBlob = new Blob([byteArray], { type: 'image/png' });

        // FormData 준비
        const filename = "clipspace-tmp_image.png";
        const formData = new FormData();
        formData.append("image", new File([myBlob], filename));
        formData.append("overwrite", "true");
        formData.append("type", "input");

        const item = {
            filename,
            subfolder: "",
            type: "input",
        };

		// ComfyApp 관련 상태 업데이트
		if (!ComfyApp.clipspace) {
			const load_image_nodes = app.graph._nodes.filter((n) => n.type.includes("Load Image") || n.type.includes("LoadImage"));
			let found_node = false;
			for (let n of load_image_nodes) {
				if (n && n.imgs[0]) 	{
					ComfyApp.copyToClipspace(n);
					ComfyApp.clipspace_return_node = null;
					found_node = true;
					break;
				}
			}	
			if (!found_node) {
				console.error('Unable copy Clipspace image:');
				return;
			}
        }
        
        if (ComfyApp.clipspace.images) {
            ComfyApp.clipspace.images[0] = item;
        }

        if (ComfyApp.clipspace.widgets) {
            const index = ComfyApp.clipspace.widgets.findIndex(obj => obj.name === 'image');
            if (index >= 0) {
                ComfyApp.clipspace.widgets[index].value = `${filename} [input]`;
            }
        }

        // 파일 업로드 및 후속 작업
        await uploadImage(item, formData);
        ComfyApp.onClipspaceEditorSave();

		find_script_load_image(width, height);
		showMessage("Info", "Created empty image to Regional Script 💬ED")
    } catch (error) {
        console.error('Error saving image:', error);
    }
}

app.registerExtension({
	name: "ED.WildcardSelect",
	nodeCreated(node, app) {
		if( node.comfyClass == "Get Booru Tag 💬ED" || node.comfyClass == "Regional Script 💬ED" || node.comfyClass == "Context To DetailerPipe") {
			node._value = "Select the LoRA to add to the text";
			node._wvalue = "Select the Wildcard to add to the text";

			var tbox_id = 2;
			var combo_id = 3;
			var has_lora = false;
			
			switch(node.comfyClass){
				case "Get Booru Tag 💬ED":
					tbox_id = 1;
					combo_id = 1;
					has_lora = false;
					break;

				case "Regional Script 💬ED":
					tbox_id = 4;
					combo_id = 4;
					has_lora = false;
					break;

				case "Context To DetailerPipe":
					tbox_id = 0;
					combo_id = 1;
					has_lora = true;
					break;
			}
			
            node.widgets[combo_id+1].callback = (value, canvas, node, pos, e) => {
				if(node.widgets[tbox_id].value != ''){
					node.widgets[tbox_id].value = node.widgets[tbox_id].value.replace(/,\s*$/, '');
					node.widgets[tbox_id].value += ', ';
				}
                node.widgets[tbox_id].value += node._wildcard_value + ",";
            }

			Object.defineProperty(node.widgets[combo_id+1], "value", {
				set: (value) => {
                    if (value !== "Select the Wildcard to add to the text")
                        node._wildcard_value = value;
                },
				get: () => { return "Select the Wildcard to add to the text"; }
			});

			Object.defineProperty(node.widgets[combo_id+1].options, "values", {
				set: (x) => {},
				get: () => {
					return wildcards_list;
				}
			});

			if(has_lora) {
				node.widgets[combo_id].callback = (value, canvas, node, pos, e) => {
					let lora_name = node._value;
					if(lora_name.endsWith('.safetensors')) {
						lora_name = lora_name.slice(0, -12);
					}

					node.widgets[tbox_id].value += `<lora:${lora_name}>`;
					if(node.widgets_values) {
						node.widgets_values[tbox_id] = node.widgets[tbox_id].value;
					}
				}

				Object.defineProperty(node.widgets[combo_id], "value", {
					set: (value) => {
							if (value !== "Select the LoRA to add to the text")
								node._value = value;
						},

					get: () => { return "Select the LoRA to add to the text"; }
				});
			}

			// Preventing validation errors from occurring in any situation.
			if(has_lora) {
				node.widgets[combo_id].serializeValue = () => { return "Select the LoRA to add to the text"; }
			}
			node.widgets[combo_id+1].serializeValue = () => { return "Select the Wildcard to add to the text"; }
		}
		
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////		
		if( node.comfyClass == "Regional Stacker 💬ED" || node.comfyClass == "Regional Processor 💬ED") {
			node._wvalue = "Create empty image";			

			const empty_image_widget = node.widgets[3];
			const width_widget = node.widgets[1];
			const height_widget = node.widgets[2];
			
            empty_image_widget.callback = (value, canvas, node, pos, e) => {
                createEmptyImage(width_widget.value, height_widget.value);
            }

			Object.defineProperty(empty_image_widget, "value", {
				set: (value) => {
                    if (value !== "Create empty image")
                        node._wildcard_value = value;
                },
				get: () => { return "Create empty image"; }
			});

			Object.defineProperty(empty_image_widget.options, "values", {
				set: (x) => {},
				get: () => {
					return ["Create empty image."];
				}
			});

			empty_image_widget.serializeValue = () => { return "Create empty image"; }
		}
	}
});
