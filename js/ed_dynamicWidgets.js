import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyDialog, $el } from "../../scripts/ui.js";
import { ComfyApp } from "../../scripts/app.js";
import { ClipspaceDialog } from "../../extensions/core/clipspace.js";

import { toggleWidget, findWidgetByName, updateNodeHeight, showMessage } from "./node_options/common/utils.js";

let wildcards_list = [];

async function load_wildcards() {
	let res = await api.fetchApi('/impact/wildcards/list');
	let data = await res.json();
	wildcards_list = data.data;
}

load_wildcards();

let dynamicWidgets_initialized = false;

const NODE_WIDGET_HANDLERS = {
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
        'set_seed_cfg_sampler': handleEfficientSamplerSetSeed_ED
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

/////////////////////////////////////////////////////////////////////////// ED
let previous_value = { sampler_ed_denoise : 0, ed_loader_vae : "", ed_loader_cfg : 0};

function getNodeFromLink(node, linkId, from="") {
    const linkInfo = app.graph.links[linkId];
    const id = from === "origin" ? linkInfo.origin_id : linkInfo.target_id;
    return node.graph.getNodeById(id);
}

function isMatchingNode(node, nodeType) {
    return node.type?.includes(nodeType);
}

function recursive_FindLinkedNode(node, nodeType) {

	function isContextNode(node) {
		return node.type && (node.type.includes('Context') || node.type === 'Wildcard Encode 💬ED' || node.type === 'TIPO Script 💬ED');
	}

	if (!node) return null;
    const links = node.outputs[0]?.links;
    if (!links) return null;

    for (const linkId of links) {
        const targetNode = getNodeFromLink(node, linkId);
		if (!targetNode) return null;

        if (isMatchingNode(targetNode, nodeType)) {
            return targetNode;
        }

        if (isContextNode(targetNode)) {
			return recursive_FindLinkedNode(targetNode, nodeType);
        }
    }
	
    return null;
}
 
// New function to handle widget visibility based on input_mode
function handleInputModeWidgetsVisibility(node, inputModeValue) {
    // Utility function to generate widget names up to a certain count
    function generateWidgetNames(baseName, count) {
        return Array.from({ length: count }, (_, i) => `${baseName}_${i + 1}`);
    }

    // Common widget groups
    // const batchWidgets = ["batch_path", "subdirectories", "batch_sort", "batch_max"];
    // const xbatchWidgets = ["X_batch_path", "X_subdirectories", "X_batch_sort", "X_batch_max"];
    // const ckptWidgets = [...generateWidgetNames("ckpt_name", 10)];
    // const clipSkipWidgets = [...generateWidgetNames("clip_skip", 10)];
    // const vaeNameWidgets = [...generateWidgetNames("vae_name", 10)];
    // const loraNameWidgets = [...generateWidgetNames("lora_name", 10)];
    const loraWtWidgets = [...generateWidgetNames("lora_wt", 10)];
    const modelStrWidgets = [...generateWidgetNames("model_str", 10)];
    const clipStrWidgets = [...generateWidgetNames("clip_str", 10)];
    // const xWidgets = ["X_batch_count", "X_first_value", "X_last_value"]
    // const yWidgets = ["Y_batch_count", "Y_first_value", "Y_last_value"]

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
function handleVisibility(node, widget, node_type) {
	const baseNamesMap = {
		"LoRA Stacker 💬ED": ["lora_name", "model_str", "clip_str", "lora_wt"],
		"Embedding Stacker 💬ED_pos": ["positive_embedding", "positive_emphasis"],
		"Embedding Stacker 💬ED_neg": ["negative_embedding", "negative_emphasis"]
    };
	const countValue = widget.value;

    const baseNames = baseNamesMap[node_type];

    for (let i = 1; i <= 9; i++) {
        const widget_1 = findWidgetByName(node, `${baseNames[0]}_${i}`);
        const widget_2 = findWidgetByName(node, `${baseNames[1]}_${i}`);
        const widget_3 = (node_type === "LoRA Stacker 💬ED") ? findWidgetByName(node, `${baseNames[2]}_${i}`) : null;
        const widget_4 = (node_type === "LoRA Stacker 💬ED") ? findWidgetByName(node, `${baseNames[3]}_${i}`) : null;

        if (i <= countValue) {

            if (node_type === "LoRA Stacker 💬ED") {				
				const inputModeValue = findWidgetByName(node, "input_mode").value;
				
				toggleWidget(node, widget_1, true);
                if (inputModeValue === "simple") {
                    toggleWidget(node, widget_2, false);   // model_str
                    toggleWidget(node, widget_3, false); // clip_str
                    toggleWidget(node, widget_4, true);  // lora_wt
                } else if (inputModeValue === "advanced") {
                    toggleWidget(node, widget_2, true);   // model_str
                    toggleWidget(node, widget_3, true);  // clip_str
                    toggleWidget(node, widget_4, false);   // lora_wt
                }
            } else if (node_type.includes("Embedding Stacker 💬ED")) {
				toggleWidget(node, widget_1, true);   // _embedding
				toggleWidget(node, widget_2, true);   // _emphasis
            }
        }
        else {
            toggleWidget(node, widget_1, false);
            toggleWidget(node, widget_2, false);
            if (widget_3) toggleWidget(node, widget_3, false);
            if (widget_4) toggleWidget(node, widget_4, false);
        }
    }
}

// In the main function where widgetLogic is called
function widgetLogic(node, widget) {
    // Retrieve the handler for the current node title and widget name
    const handler = NODE_WIDGET_HANDLERS[node.comfyClass]?.[widget.name];
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
	const sampler_ed = recursive_FindLinkedNode(node, 'KSampler (Efficient) 💬ED')	

	if (!sampler_ed?.toggleWidgetByProperty) return;
	const target_wiget = findWidgetByName(sampler_ed, "denoise");
	
    if (widget.value == '✍️ Txt2Img') {
		previous_value.sampler_ed_denoise = restore_prev_value(target_wiget, 1.0, previous_value.sampler_ed_denoise, true);
		sampler_ed.toggleWidgetByProperty(false);
    } else if(widget.value == '🎨 Inpaint(MaskDetailer)') {		
        previous_value.sampler_ed_denoise = restore_prev_value(target_wiget, 1.0, previous_value.sampler_ed_denoise);
		sampler_ed.toggleWidgetByProperty(true);
    }
	else{
		previous_value.sampler_ed_denoise = restore_prev_value(target_wiget, 1.0, previous_value.sampler_ed_denoise);
		sampler_ed.toggleWidgetByProperty(false);
	}	
}

// Efficient Loader ED Flux Mode Handlers
function handleEfficientLoaderFluxMode_ED(node, widget) {
	const mute_n1_type = ["UnetLoaderGGUF", "CLIPLoaderGGUF", "DualCLIPLoaderGGUF", "TripleCLIPLoaderGGUF", "UnetLoaderGGUFAdvanced", "UNETLoader", "DualCLIPLoader"];
	const mute_n2_type = ["FluxGuidance"];
	const bypass_n_type = ["LoRA Stacker 💬ED", "Embedding Stacker 💬ED"];
	const opposite_n_type = ["FreeU", "FreeU_V2", "ModelSamplingDiscrete", "RescaleCFG"];
	
	if (!dynamicWidgets_initialized) return;
	
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
		let w_clipskip = findWidgetByName(node, 'clip_skip')
		w_clipskip.value = 0;
		mute1_group.forEach(n => n.mode = 2);
		//mute2_group.forEach(n => n.mode = 0);
		//bypass_group.forEach(n => n.mode = 4);
		opposite_group.forEach(n => n.mode = 4);
		
		let w =  findWidgetByName(node, 'cfg');
		previous_value.ed_loader_cfg = restore_prev_value(w, 1.0, previous_value.ed_loader_cfg, true);

		w =  findWidgetByName(node, 'vae_name');
		let val = w.options.values.find(isFlux);
		if ((val) && !isFlux(w.value)) {
			previous_value.ed_loader_vae = w.value;
			w.value = val;				
		}
    }else if (value == '🔌 model_opt input') {
		let w_clipskip = findWidgetByName(node, 'clip_skip')
		w_clipskip.value = 0;
		mute1_group.forEach(n => n.mode = 0);
		//mute2_group.forEach(n => n.mode = 0);
		//bypass_group.forEach(n => n.mode = 4);
		opposite_group.forEach(n => n.mode = 4);
		
		let w =  findWidgetByName(node, 'cfg');
		previous_value.ed_loader_cfg = restore_prev_value(w, 1.0, previous_value.ed_loader_cfg, true);

		w =  findWidgetByName(node, 'vae_name');
		let val = w.options.values.find(isFlux);
		if ((val) && !isFlux(w.value)) {
			previous_value.ed_loader_vae = w.value;
			w.value = val;				
		}
    } else {		
        let w = findWidgetByName(node, 'clip_skip')
		if (w.value == 0) w.value = -2;
		mute1_group.forEach(n => n.mode = 2);
		//mute2_group.forEach(n => n.mode = 2);
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
    }
}

// Sampler Set Seed ED Handlers
function handleEfficientSamplerSetSeed_ED(node, widget) {
	const opened = !(widget.value === "from context");
    
    toggleWidget(node, findWidgetByName(node, 'seed'), opened);
	toggleWidget(node, findWidgetByName(node, 'control_after_generate'), opened);
    toggleWidget(node, findWidgetByName(node, 'cfg'), opened);
	toggleWidget(node, findWidgetByName(node, 'sampler_name'), opened);
	toggleWidget(node, findWidgetByName(node, 'scheduler'), opened);
	//toggleWidget(node, findWidgetByName(node, 'batch_size'), opened);
}

// Reginal ScriptED Handlers
function handleReginalScript_ED(node, widget) {
    toggleWidget(node, findWidgetByName(node, 'blur_mask_kernel_size'), widget.value);
	toggleWidget(node, findWidgetByName(node, 'blur_mask_sigma'), widget.value);
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
		showMessage("Error", error.replaceAll("ERROR: ", ""));
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
				showMessage("Success", 'Danbooru tags are successfully loaded');
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
				showMessage("Success", 'Gelbooru tags are successfully loaded');
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
	const opened = !(widget.value.includes("not upscale"));
    
    toggleWidget(node, findWidgetByName(node, 'width'), opened);
	toggleWidget(node, findWidgetByName(node, 'height'), opened);
	toggleWidget(node, findWidgetByName(node, 'keep_proportions'), opened);
}

// UltimateSDUpscaler ED Handlers
function handleUltimateSDUpscalerTileSize_ED(node, widget) {
    if (widget.value == 'Image size' || widget.value == 'Canvas size') {
        toggleWidget(node, findWidgetByName(node, 'tile_width'));
        toggleWidget(node, findWidgetByName(node, 'tile_height'));
    } else {
        toggleWidget(node, findWidgetByName(node, 'tile_width'), true);
        toggleWidget(node, findWidgetByName(node, 'tile_height'), true);
    }
}

// LoRA Stacker ED Handlers
function handleLoRAStackerEDInputMode(node, widget) {
    handleInputModeWidgetsVisibility(node, widget.value);
    handleVisibility(node, findWidgetByName(node, "lora_count"), "LoRA Stacker 💬ED");
	updateNodeHeight(node);
}

function handleLoRAStackerEDLoraCount(node, widget) {
    handleVisibility(node, widget, "LoRA Stacker 💬ED");
	updateNodeHeight(node);
}

// Embedding Stacker ED Handlers
function handleEmbeddingStacker(node, widget) {
	const posORneg = widget.name.substr(0, 3);
	handleVisibility(node, widget, "Embedding Stacker 💬ED_"+ posORneg);
	updateNodeHeight(node);
}

async function createEmptyImage(width, height, color="white") {
	
	function findPreviousNode(node, nodeType) {
		if (!node) return null;

		const linkId = node.inputs?.[2]?.link;
		if (!linkId) return null;

		const targetNode = getNodeFromLink(node, linkId, "origin");
		return (targetNode && isMatchingNode(targetNode, nodeType)) ? targetNode : null;
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

function getBooruTagRegionalScript(node){

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


app.registerExtension({
    name: "ED.DynamicWidgets",
    nodeCreated(node) {
		
		getBooruTagRegionalScript(node);	
		if (!NODE_WIDGET_HANDLERS[node.comfyClass]) return;
		
		if (node.widgets){
			for (const w of node.widgets) {
				if (!NODE_WIDGET_HANDLERS[node.comfyClass][w.name]) continue;
				
				let widgetValue = w.value;				
				widgetLogic(node, w);	

				// Define getters and setters for widget values
				Object.defineProperty(w, 'value', {
					get() {
						return widgetValue;
					},
					set(newVal) {
						if (newVal !== widgetValue) {
							widgetValue = newVal;
							widgetLogic(node, w);
						}
					}
				});
			}
		}
    },
	async setup() {
        dynamicWidgets_initialized = true;
    },
});

