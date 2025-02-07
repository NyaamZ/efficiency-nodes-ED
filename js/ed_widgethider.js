import { app } from "../../scripts/app.js";
//import { bo as useToastStore } from "../../assets/index-DIU5yZe9.js";

let origProps = {};
let initialized = false;

function show_message(short_msg, detail_msg, node=null) {
	if (node) {
		console.log("## " + detail_msg + " ID:" + node.id);
	} else {
		console.log("## " + detail_msg);	
	}
	// useToastStore().add({
        // severity: short_msg.toLowerCase(),
        // summary: short_msg,
        // detail: detail_msg,
        // life: 3e3
      // });
}

export const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

const doesInputWithNameExist = (node, name) => {
    return node.inputs ? node.inputs.some((input) => input.name === name) : false;
};

const HIDDEN_TAG = "tschide";
// Toggle Widget + change size
export function toggleWidget(node, widget, show = false, suffix = "") {
    if (!widget || doesInputWithNameExist(node, widget.name)) return;

    // Store the original properties of the widget if not already stored
    if (!origProps[widget.name]) {
        origProps[widget.name] = { origType: widget.type, origComputeSize: widget.computeSize };
    }

    const origSize = node.size;

    // Set the widget type and computeSize based on the show flag
    widget.type = show ? origProps[widget.name].origType : HIDDEN_TAG + suffix;
    widget.computeSize = show ? origProps[widget.name].origComputeSize : () => [0, -4];

    // Recursively handle linked widgets if they exist
    widget.linkedWidgets?.forEach(w => toggleWidget(node, w, ":" + widget.name, show));

    // Calculate the new height for the node based on its computeSize method
    const newHeight = node.computeSize()[1];
    node.setSize([node.size[0], newHeight]);
}

const WIDGET_HEIGHT = 24;
// Use for Multiline Widget Nodes (aka Efficient Loaders)
function toggleWidget_2(node, widget, show = false, suffix = "") {
    if (!widget || doesInputWithNameExist(node, widget.name)) return;
    
    const isCurrentlyVisible = widget.type !== HIDDEN_TAG + suffix;
    if (isCurrentlyVisible === show) return; // Early exit if widget is already in the desired state

    if (!origProps[widget.name]) {
        origProps[widget.name] = { origType: widget.type, origComputeSize: widget.computeSize };
    }

    widget.type = show ? origProps[widget.name].origType : HIDDEN_TAG + suffix;
    widget.computeSize = show ? origProps[widget.name].origComputeSize : () => [0, -4];

    if (initialized){
        const adjustment = show ? WIDGET_HEIGHT : -WIDGET_HEIGHT;
        node.setSize([node.size[0], node.size[1] + adjustment]);
    }
}

/////////////////////////////////////////////////////////////////////////// ED
let previous_value = { ed_sampler_noise : 0, ed_loader_vae : "", ed_loader_cfg : 0};

/* function find_neighbor_node(node, nodetype){
	const linkk = node.outputs[0].links;
	if (linkk) {
		for (const l of linkk) {
			const linkInfo = app.graph.links[l];
			const n = node.graph.getNodeById(linkInfo.target_id);
			//console.log("ED_log node type:" + n.type);	
			if ((n)&&n.type.indexOf(nodetype) != -1) {
				return n;
			}
			else if(n.type.indexOf('Context') != -1 || n.type == "Wildcard Encode 💬ED") {
				const linkctx = n.outputs[0].links;
				if (linkctx) {
					for (const l of linkctx) {
						const linkInfo_ctx = app.graph.links[l];
						const n_ctx = n.graph.getNodeById(linkInfo_ctx.target_id);
						//console.log("ED_log node type:" + n.type);	
						if ((n_ctx) && n_ctx.type.indexOf(nodetype) != -1) {
							return n_ctx;
						}
					}
				}
			}
		}		
	}
	return null;
}
 */
 
 function findNeighborNode(node, nodeType) {
	if (!node) return null;
    const links = node.outputs[0]?.links;
    if (!links) return null;

    for (const linkId of links) {
        const targetNode = getNodeFromLink(node, linkId);

        if (isMatchingNode(targetNode, nodeType)) {
            return targetNode;
        }

        if (isContextNode(targetNode)) {
            const contextLinks = targetNode.outputs[0]?.links;

            if (!contextLinks) continue;

            for (const contextLinkId of contextLinks) {
                const contextNode = getNodeFromLink(targetNode, contextLinkId);

                if (isMatchingNode(contextNode, nodeType)) {
                    return contextNode;
                }
            }
        }
    }

    return null;
}

function getNodeFromLink(node, linkId) {
    const linkInfo = app.graph.links[linkId];
    return node.graph.getNodeById(linkInfo.target_id);
}

function isMatchingNode(node, nodeType) {
    return node.type && node.type.includes(nodeType);
}

function isContextNode(node) {
    return node.type && (node.type.includes('Context') || node.type === 'Wildcard Encode 💬ED');
}

 
// New function to handle widget visibility based on input_mode
function handleInputModeWidgetsVisibility(node, inputModeValue) {
    // Utility function to generate widget names up to a certain count
    function generateWidgetNames(baseName, count) {
        return Array.from({ length: count }, (_, i) => `${baseName}_${i + 1}`);
    }

    // Common widget groups
    const batchWidgets = ["batch_path", "subdirectories", "batch_sort", "batch_max"];
    const xbatchWidgets = ["X_batch_path", "X_subdirectories", "X_batch_sort", "X_batch_max"];
    const ckptWidgets = [...generateWidgetNames("ckpt_name", 50)];
    const clipSkipWidgets = [...generateWidgetNames("clip_skip", 50)];
    const vaeNameWidgets = [...generateWidgetNames("vae_name", 50)];
    const loraNameWidgets = [...generateWidgetNames("lora_name", 50)];
    const loraWtWidgets = [...generateWidgetNames("lora_wt", 50)];
    const modelStrWidgets = [...generateWidgetNames("model_str", 50)];
    const clipStrWidgets = [...generateWidgetNames("clip_str", 50)];
    const xWidgets = ["X_batch_count", "X_first_value", "X_last_value"]
    const yWidgets = ["Y_batch_count", "Y_first_value", "Y_last_value"]

    const nodeVisibilityMap = {
		"LoRA Stacker 💬ED": {
            "simple": [...modelStrWidgets, ...clipStrWidgets],
            "advanced": [...loraWtWidgets]
        },
    };

    const inputModeVisibilityMap = nodeVisibilityMap[node.comfyClass];
    
    if (!inputModeVisibilityMap || !inputModeVisibilityMap[inputModeValue]) return;

    // Reset all widgets to visible
    for (const key in inputModeVisibilityMap) {
        for (const widgetName of inputModeVisibilityMap[key]) {
            const widget = findWidgetByName(node, widgetName);
            toggleWidget(node, widget, true);
        }
    }

    // Hide the specific widgets for the current input_mode value
    for (const widgetName of inputModeVisibilityMap[inputModeValue]) {
        const widget = findWidgetByName(node, widgetName);
        toggleWidget(node, widget, false);
    }
}

// Handle multi-widget visibilities
function handleVisibility(node, countValue, node_type) {
    const inputModeValue = findWidgetByName(node, "input_mode").value;
    const baseNamesMap = {
		"LoRA Stacker 💬ED": ["lora_name", "model_str", "clip_str", "lora_wt"]
    };

    const baseNames = baseNamesMap[node_type];

    const isBatchMode = inputModeValue.includes("Batch");
    if (isBatchMode) {countValue = 0;}

    for (let i = 1; i <= 50; i++) {
        const nameWidget = findWidgetByName(node, `${baseNames[0]}_${i}`);
        const firstWidget = findWidgetByName(node, `${baseNames[1]}_${i}`);
        const secondWidget = findWidgetByName(node, `${baseNames[2]}_${i}`);
        const thirdWidget = (node_type === "LoRA Stacker" || node_type === "LoRA Stacker 💬ED") ? findWidgetByName(node, `${baseNames[3]}_${i}`) : null;

        if (i <= countValue) {
            toggleWidget(node, nameWidget, true);

            if (node_type === "LoRA Stacker 💬ED") {
                if (inputModeValue === "simple") {
                    toggleWidget(node, firstWidget, false);   // model_str
                    toggleWidget(node, secondWidget, false); // clip_str
                    toggleWidget(node, thirdWidget, true);  // lora_wt
                } else if (inputModeValue === "advanced") {
                    toggleWidget(node, firstWidget, true);   // model_str
                    toggleWidget(node, secondWidget, true);  // clip_str
                    toggleWidget(node, thirdWidget, false);   // lora_wt
                }
            } else if (node_type === "Checkpoint") {
                if (inputModeValue.includes("ClipSkip")){toggleWidget(node, firstWidget, true);}
                if (inputModeValue.includes("VAE")){toggleWidget(node, secondWidget, true);}
            } else if (node_type === "LoRA") {
                if (inputModeValue.includes("Weights")){
                    toggleWidget(node, firstWidget, true);
                    toggleWidget(node, secondWidget, true);
                }
            }
        }
        else {
            toggleWidget(node, nameWidget, false);
            toggleWidget(node, firstWidget, false);
            toggleWidget(node, secondWidget, false);
            if (thirdWidget) {toggleWidget(node, thirdWidget, false);}
        }
    }
}

/* // Handle simple widget visibility based on a count
function handleWidgetVisibility(node, thresholdValue, widgetNamePrefix, maxCount) {
    for (let i = 1; i <= maxCount; i++) {
        const widget = findWidgetByName(node, `${widgetNamePrefix}${i}`);
        if (widget) {
            toggleWidget(node, widget, i <= thresholdValue);
        }
    }
}
 */
// Create a map of node titles to their respective widget handlers
const nodeWidgetHandlers = {
    "Efficient Loader 💬ED": {
		'paint_mode': handleEfficientLoaderPaintMode_ED,
		'ckpt_name': handleEfficientLoaderFluxMode_ED
    },
    "KSampler (Efficient) 💬ED": {
        'set_seed_cfg_sampler': handleEfficientSamplerSetSeed_ED
    },
    "KSampler Text 💬ED": {
        'set_seed_cfg_sampler': handleEfficientSamplerSetSeed_ED
    },
    "Load Image 💬ED": {
        'upscale_method': handleLoadImage_ED
    },
	"FaceDetailer 💬ED": {
        'set_seed_cfg_sampler': handleEfficientSamplerSetSeed_ED
    },
	"MaskDetailer 💬ED": {
        'set_seed_cfg_sampler_batch': handleEfficientSamplerSetSeed_ED
    },
	"Detailer (SEGS) 💬ED": {
        'set_seed_cfg_sampler': handleEfficientSamplerSetSeed_ED
    },
    "Embedding Stacker 💬ED": {
        'positive_embeddings_count': handleEmbeddingStacker,
		'negative_embeddings_count': handleEmbeddingStacker
    },
	"Ultimate SD Upscale 💬ED": {
        'set_seed_cfg_sampler': handleEfficientSamplerSetSeed_ED,
		'set_tile_size_from': handleUltimateSDUpscalerTileSize_ED
    },
	"LoRA Stacker 💬ED": {
        'input_mode': handleLoRAStackerEDInputMode,
        'lora_count': handleLoRAStackerEDLoraCount
    },
	"SUPIR Sampler 💬ED": {
        'set_seed_cfg_sampler': handleEfficientSamplerSetSeed_ED
    },
	"Refiner Script 💬ED": {
        'set_seed_cfg_sampler': handleEfficientSamplerSetSeed_ED
    },
	"Regional Script 💬ED": {
		'url': handleGetBooruTag,
        'use_blur_mask': handleReginalScript_ED
    },
	"Get Booru Tag 💬ED": {
        'url': handleGetBooruTag
    },
};

// In the main function where widgetLogic is called
function widgetLogic(node, widget) {
    // Retrieve the handler for the current node title and widget name
    const handler = nodeWidgetHandlers[node.comfyClass]?.[widget.name];
    if (handler) {
        handler(node, widget);
    }
}

// function restore previos value
function restore_prev_value(widget, compare_value, prev_value, change = false) {	
	if (widget) {
		if (change){
			if (widget.value != compare_value) { 
				var prev_val = widget.value;
				widget.value = compare_value;
				return prev_val;
			}
		}else{
			if ((widget.value == compare_value) && (prev_value)) {
				widget.value = prev_value;			
			}
		}
	}
	return prev_value;
}

// Efficient Loader ED Paint Mode Handlers
function handleEfficientLoaderPaintMode_ED(node, widget) {
	
	const n_node = findNeighborNode(node, 'KSampler')	
	if (n_node == null)
		return;
	const is_ed_sampler = (n_node.type == "KSampler (Efficient) 💬ED")
	const target_wiget = findWidgetByName(n_node, "denoise");
	
    if (widget.value == '✍️ Txt2Img') {
		previous_value.ed_sampler_noise = restore_prev_value(target_wiget, 1.0, previous_value.ed_sampler_noise, true);
		if (is_ed_sampler && (typeof n_node.toggleWidgetByProperty === 'function')) 
			n_node.toggleWidgetByProperty(false);
    } else if(widget.value == '🎨 Inpaint(MaskDetailer)') {		
        previous_value.ed_sampler_noise = restore_prev_value(target_wiget, 1.0, previous_value.ed_sampler_noise);
		if (is_ed_sampler && (typeof n_node.toggleWidgetByProperty === 'function')) 
			n_node.toggleWidgetByProperty(true);
    }
	else{
		previous_value.ed_sampler_noise = restore_prev_value(target_wiget, 1.0, previous_value.ed_sampler_noise);
		if (is_ed_sampler && (typeof n_node.toggleWidgetByProperty === 'function')) 
			n_node.toggleWidgetByProperty(false);
	}	
}

// Efficient Loader ED Flux Mode Handlers
function handleEfficientLoaderFluxMode_ED(node, widget) {
	const mute_n1_type = ["UnetLoaderGGUF", "CLIPLoaderGGUF", "DualCLIPLoaderGGUF", "TripleCLIPLoaderGGUF", "UnetLoaderGGUFAdvanced", "UNETLoader", "DualCLIPLoader"];
	const mute_n2_type = ["FluxGuidance"];
	const bypass_n_type = ["LoRA Stacker 💬ED", "Embedding Stacker 💬ED"];
	const opposite_n_type = ["FreeU", "FreeU_V2"];
	const adjustment  = node.size[1];
	
	function add_group(type_list){
		let group = [];
		type_list.forEach(function (t) {
			let i = app.graph._nodes.find((n) => n.type === t);
			if (i) group.push(i);
		});	
		return group;
	}
	
	let mute1_group = add_group(mute_n1_type);
	let mute2_group = add_group(mute_n2_type);
	let bypass_group = add_group(bypass_n_type);
	let opposite_group = add_group(opposite_n_type);
	
	let value = widget.value;
	if (value?.content) {
		value = value.content;
	}
	
	function isFlux(value)  { if(value.toLowerCase().indexOf('flux') != -1 )  return true; }
	function isSdxl(value)  { if(value.toLowerCase().indexOf('sdxl') != -1 )  return true; }
	
	if (isFlux(value)) { //ckpt_name is flux
		//toggleWidget_2(node, findWidgetByName(node, 'clip_skip'));
		let w_clipskip = findWidgetByName(node, 'clip_skip')
		w_clipskip.value = 0;
		mute1_group.forEach(n => n.mode = 2);
		mute2_group.forEach(n => n.mode = 0);
		bypass_group.forEach(n => n.mode = 4);
		opposite_group.forEach(n => n.mode = 2);
		
		let w =  findWidgetByName(node, 'cfg');
		previous_value.ed_loader_cfg = restore_prev_value(w, 1.0, previous_value.ed_loader_cfg, true);

		w =  findWidgetByName(node, 'vae_name');
		let val = w.options.values.find(isFlux);
		if ((val) && !isFlux(w.value)) {
			previous_value.ed_loader_vae = w.value;
			w.value = val;				
		}
		if (node.size[1] < adjustment) node.setSize([node.size[0], adjustment]);
    }else if (value == '🔌 model_opt input') {
		//toggleWidget_2(node, findWidgetByName(node, 'clip_skip'));
		let w_clipskip = findWidgetByName(node, 'clip_skip')
		w_clipskip.value = 0;
		mute1_group.forEach(n => n.mode = 0);
		mute2_group.forEach(n => n.mode = 0);
		bypass_group.forEach(n => n.mode = 4);
		opposite_group.forEach(n => n.mode = 2);
		
		let w =  findWidgetByName(node, 'cfg');
		previous_value.ed_loader_cfg = restore_prev_value(w, 1.0, previous_value.ed_loader_cfg, true);

		w =  findWidgetByName(node, 'vae_name');
		let val = w.options.values.find(isFlux);
		if ((val) && !isFlux(w.value)) {
			previous_value.ed_loader_vae = w.value;
			w.value = val;				
		}
		if (node.size[1] < adjustment) node.setSize([node.size[0], adjustment]);
    } else {		
        let w = findWidgetByName(node, 'clip_skip')
		//toggleWidget_2(node, w, true);
		if (w.value == 0) w.value = -2;
		mute1_group.forEach(n => n.mode = 2);
		mute2_group.forEach(n => n.mode = 2);
		//bypass_group.forEach(n => n.mode = 0);
		//opposite_group.forEach(n => n.mode = 0);
		
		w =  findWidgetByName(node, 'cfg');
		previous_value.ed_loader_cfg = restore_prev_value(w, 1.0, previous_value.ed_loader_cfg);
		
		w =  findWidgetByName(node, 'vae_name');
		let sdxl_val = w.options.values.find(isSdxl);
		if ((sdxl_val) && isFlux(w.value)) {
			if ((previous_value.ed_loader_vae) && !isFlux(previous_value.ed_loader_vae)) w.value = previous_value.ed_loader_vae;
			else w.value = sdxl_val;
		}
		node.setSize([node.size[0], adjustment]);
    }
}

// Sampler Set Seed ED Handlers
function handleEfficientSamplerSetSeed_ED(node, widget) {
	const adjustment  = node.size[1];
	const opened = !(widget.value === "from context");
    
    toggleWidget(node, findWidgetByName(node, 'seed'), opened);
	toggleWidget(node, findWidgetByName(node, 'control_after_generate'), opened);
    toggleWidget(node, findWidgetByName(node, 'cfg'), opened);
	toggleWidget(node, findWidgetByName(node, 'sampler_name'), opened);
	toggleWidget(node, findWidgetByName(node, 'scheduler'), opened);
	toggleWidget(node, findWidgetByName(node, 'batch_size'), opened);
	if (node.size[1] < adjustment) 	node.setSize([node.size[0], adjustment]);
}

// Reginal ScriptED Handlers
function handleReginalScript_ED(node, widget) {
	const adjustment  = node.size[1];
    toggleWidget(node, findWidgetByName(node, 'blur_mask_kernel_size'), widget.value);
	toggleWidget(node, findWidgetByName(node, 'blur_mask_sigma'), widget.value);
	if (node.size[1] < adjustment) 	node.setSize([node.size[0], adjustment]);
}

// Get Booru Tag ED Handlers
async function handleGetBooruTag(node, widget) {
	function htmlUnescape (string) {
		let str = string;
		str = str.replaceAll("&amp;", "&");
		str = str.replaceAll('&quot;', '"');
		str = str.replaceAll("&#035;", "#");
		str = str.replaceAll("&#039;", "'");
		str = str.replaceAll("&lt;", "<");
		str = str.replaceAll("&gt;", ">");
		return str;
	}
	
	if (!(widget.value.includes('danbooru') || widget.value.includes('gelbooru'))) return;

	let tagsWidget
	if (node.comfyClass == "Get Booru Tag 💬ED") 
		tagsWidget = findWidgetByName(node, "text_b");
	if (node.comfyClass == "Regional Script 💬ED")
		tagsWidget = findWidgetByName(node, "prompt");
	
	const proxy = 'https://corsproxy.io/?';

    // 태그 설정 함수
    function setTags(tags) {
		let tag_data = htmlUnescape(tags.replaceAll(' ', ', ') + ",");
        tagsWidget.value = tag_data;
    }
    // 에러 표시
    function showError(error) {
        tagsWidget.value = '// ' + error + '\n\n' + tagsWidget.value;
		show_message("Error", error.replaceAll("ERROR: ", "") , node);
    }

    // 에러 처리 및 데이터 요청 함수
    async function fetchData(url) {
        try {
            const req = await fetch(url);
            if (!req.ok) throw new Error(`HTTP Error! Status Code: ${req.status}`);
            return await req.json();
        } catch (error) {
            showError(error);
            return null;
        }
    }

    if (widget.value.includes('danbooru')) {
        const baseDanbooruUrl = "https://danbooru.donmai.us/";
        const match = /posts\/(\d+)/.exec(widget.value);

        if (match) {
            const url = baseDanbooruUrl + match[0] + '.json';
            const data = await fetchData(url);
            if (data) {
				let tags = ""
                if (data.tag_string_artist) tags += "/*artist*/" + data.tag_string_artist + " \n";
				if (data.tag_string_character) tags += "/*character*/" + data.tag_string_character + " \n";
				if (data.tag_string_copyright) tags += "/*copyright*/" + data.tag_string_copyright + " \n";
				if (data.tag_string_general) { 
					tags += "\n" + data.tag_string_general;
				} else {
					showError('ERROR: Tags was not found in JSON file.');
				}
				setTags(tags);
				widget.value = widget.value.replaceAll("danbooru", "Danbooru");
				console.log('Tags loading success :\n' + url );
				show_message("Success", 'Danbooru tags loading is successful', node);
            } else {
				showError('ERROR: Tags was not found in JSON file.');
			}
        } else {
            showError('ERROR: ID was not found in Danbooru URL.');
        }
    }
    else if (widget.value.includes('gelbooru')) {
        const baseGelbooruUrl = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&pid=38&";
        const match = /id=(\d+)/.exec(widget.value);

        if (match) {
			const url = proxy + baseGelbooruUrl + match[0];
            const data = await fetchData(url);
            if (data && data.post && data.post[0]) {
                setTags(data.post[0].tags);
				widget.value = widget.value.replaceAll("gelbooru", "Gelbooru");
				console.log('Tags loading success :\n' + url );
				show_message("Success", 'Gelbooru tags loading is successful', node);
            } else {
				showError('ERROR: Tags was not found in JSON file.');
			}
        } else {
            showError('ERROR: ID was not found in Gelbooru URL.');
        }
    }	
}

// LoadImage ED Handlers
function handleLoadImage_ED(node, widget) {
	const adjustment  = node.size[1];
	const opened = !(widget.value.includes("not upscale"));
    
    toggleWidget(node, findWidgetByName(node, 'width'), opened);
	toggleWidget(node, findWidgetByName(node, 'height'), opened);
	toggleWidget(node, findWidgetByName(node, 'keep_proportions'), opened);
	if (node.size[1] < adjustment) 	node.setSize([node.size[0], adjustment]);
}

function handleUltimateSDUpscalerTileSize_ED(node, widget) {
    if (widget.value == 'Image size' || widget.value == 'Canvas size') {       
		const adjustment  = node.size[1];
        toggleWidget(node, findWidgetByName(node, 'tile_width'));
        toggleWidget(node, findWidgetByName(node, 'tile_height'));
		node.setSize([node.size[0], adjustment]);
    } else {
		const adjustment  = node.size[1];
        toggleWidget(node, findWidgetByName(node, 'tile_width'), true);
        toggleWidget(node, findWidgetByName(node, 'tile_height'), true);
		if (node.size[1] < adjustment) node.setSize([node.size[0], adjustment]);
    }
}

// Embedding Stacker ED Handlers
function handleEmbeddingStacker(node, widget) {
	const posORneg = widget.name.substr(0, 8);
	//console.log("widget.name.substr:" + posORneg);

    for (let i = 1; i <= 9; i++) {
        const firstWidget = findWidgetByName(node, `${posORneg}_embedding_${i}`);
        const secondWidget = findWidgetByName(node, `${posORneg}_emphasis_${i}`);

        if (i <= widget.value) {
			toggleWidget(node, firstWidget, true);   
            toggleWidget(node, secondWidget, true);
        }
        else {
            toggleWidget(node, firstWidget, false);
            toggleWidget(node, secondWidget, false);
        }
    }
}

// LoRA Stacker ED Handlers
function handleLoRAStackerEDInputMode(node, widget) {
    handleInputModeWidgetsVisibility(node, widget.value);
    handleVisibility(node, findWidgetByName(node, "lora_count").value, "LoRA Stacker 💬ED");
}

function handleLoRAStackerEDLoraCount(node, widget) {
    handleVisibility(node, widget.value, "LoRA Stacker 💬ED");
}


app.registerExtension({
    name: "efficiency_ED.ed_widgethider",
    nodeCreated(node) {
        for (const w of node.widgets || []) {
            let widgetValue = w.value;

            // Store the original descriptor if it exists
            let originalDescriptor = Object.getOwnPropertyDescriptor(w, 'value');
			if (!originalDescriptor) {
				originalDescriptor = Object.getOwnPropertyDescriptor(w.constructor.prototype, 'value');
			}

            widgetLogic(node, w);

            Object.defineProperty(w, 'value', {
                get() {
                    // If there's an original getter, use it. Otherwise, return widgetValue.
                    let valueToReturn = originalDescriptor && originalDescriptor.get
                        ? originalDescriptor.get.call(w)
                        : widgetValue;

                    return valueToReturn;
                },
                set(newVal) {

                    // If there's an original setter, use it. Otherwise, set widgetValue.
                    if (originalDescriptor && originalDescriptor.set) {
                        originalDescriptor.set.call(w, newVal);
                    } else {
                        widgetValue = newVal;
                    }

                    widgetLogic(node, w);
                }
            });
        }
        setTimeout(() => {initialized = true;}, 500);
    }
});

