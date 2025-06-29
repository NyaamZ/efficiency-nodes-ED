import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyDialog, $el } from "../../scripts/ui.js";
import { ComfyApp } from "../../scripts/app.js";
import { ClipspaceDialog } from "../../extensions/core/clipspace.js";

import { toggleWidget, findWidgetByName, updateNodeHeight, showMessage, fetchJson } from "./node_options/common/utils.js";

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
let gelApiKey = "";
async function handleGetBooruTag(node, widget) {

	function htmlUnescape (string) {
		let str = string;
		str = str.replaceAll("&amp;", "&");
		str = str.replaceAll('&quot;', '"');
		str = str.replaceAll("&#035;", "#");
		str = str.replaceAll("&#039;", "'");
		str = str.replaceAll("&lt;", "<");
		str = str.replaceAll("&gt;", ">");
		str = str.replaceAll(/\(/g, "\\(");
		str = str.replaceAll(/\)/g, "\\)");
		return str;
	}

	function updateTagsAndNotify(tags, booruSite, widget) {
		if (!tags) return showError('ERROR: Tags not found in JSON file.');
		if (typeof tags !== 'string') return showError('ERROR: Tags are not string.');

		setTags(tags);
		const capitalizedSite = capitalizeFirstLetter(booruSite);
		widget.value = widget.value.replaceAll(booruSite, capitalizedSite);

		showMessage("Success", `${capitalizedSite} tags are successfully loaded`);
	}

	function capitalizeFirstLetter(text) {
		return text.charAt(0).toUpperCase() + text.slice(1);
	}

    // 태그 설정 함수
    function setTags(tags) {
		if (tagsWidget) {
			let tag_data = htmlUnescape(tags.replaceAll(' ', ', ') + ",");
			tagsWidget.value = tag_data;
		}		
    }
    // 에러 표시
    function showError(error, showTag=false) {
        // if (showTag) tagsWidget.value = '// ' + error + '\n\n' + tagsWidget.value;
		showMessage("Error", error);
    }

    // 에러 처리 및 데이터 요청 함수
    async function fetchData(url) {
        try {
			console.log(`Fetching from: ${url}`)
            const req = await fetch(url);
            if (!req.ok) throw new Error(`HTTP Error! Status Code: ${req.status}`);
            return await req.json();
        } catch (error) {
            showError(error, true);
            return null;
        }
    }

	function getDanbooruTags(data) {
		if (!data) return null;
		let tags = "";
		if (data.tag_string_artist) tags += "/*artist*/" + data.tag_string_artist + " \n";
		if (data.tag_string_character) tags += "/*character*/" + data.tag_string_character + " \n";
		if (data.tag_string_copyright) tags += "/*copyright*/" + data.tag_string_copyright + " \n";
		tags += data.tag_string_general || "";
		return tags;
	}

	const booruDict = {
		danbooru: {
			type: "danbooru",
			base_url: "https://danbooru.donmai.us/posts/",
			func: (data) => getDanbooruTags(data), },
		aibooru: {
			type: "danbooru",
			base_url: "https://aibooru.online/posts/",
			func: (data) => getDanbooruTags(data), },
		gelbooru: {
			type: "gelbooru",
			base_url: "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1" + gelApiKey + "&id=",
			func: (data) => data?.post?.[0]?.tags, },
		safebooru: {
			type: "gelbooru",
			base_url: "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&id=",
			func: (data) => data?.[0]?.tags, },
		xbooru: {
			type: "gelbooru",
			base_url: "https://xbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=",
			func: (data) => data?.[0]?.tags, },
		konachan: {
			type: "moebooru",
			base_url: "https://konachan.net/post.json?tags=id:",
			func: (data) => data?.[0]?.tags, },
		yande: {
			type: "moebooru",
			base_url: "https://yande.re/post.json?tags=id:",
			func: (data) => data?.[0]?.tags, },
	};

	if (!widget.value || widget.value === "None" || /[A-Z]/.test(widget.value.slice(0, 10))) return;

	let tagsWidget
	if (node.comfyClass == "Get Booru Tag 💬ED") 
		tagsWidget = findWidgetByName(node, "text_b");
	if (node.comfyClass == "Regional Script 💬ED")
		tagsWidget = findWidgetByName(node, "prompt");

	let booru_name = Object.keys(booruDict).find(key => widget.value.includes(key));
	if (!booru_name) return showError('ERROR: No matching booru found.');

	const { type, base_url, func } = booruDict[booru_name];
	const proxy = 'https://corsproxy.io/?';

	// danbooru
	if (type === "danbooru") {
		const match = /posts\/(\d+)/.exec(widget.value);
		if (!match) return showError(`ERROR: ID not found in ${booru_name} URL.`);

		const url = base_url + match[1] + '.json';
		const data = await fetchData(url);
		const tags = func(data);
		
		updateTagsAndNotify(tags, booru_name, widget);
	
	// gelbooru
	} else if (type === "gelbooru") {
		const match = /id=(\d+)/.exec(widget.value);
		if (!match) return showError(`ERROR: ID not found in ${booru_name} URL.`);

		const url = proxy + base_url + match[1];
		const data = await fetchData(url);
		const tags = func(data);

		updateTagsAndNotify(tags, booru_name, widget);
	
	// moebooru
	} else if (type === "moebooru") {
		const match = /\/show\/(\d+)/.exec(widget.value);
		if (!match) return showError(`ERROR: ID not found in ${booru_name} URL.`);

		const url = proxy + base_url + match[1];
		const data = await fetchData(url);
		const tags = func(data);

		updateTagsAndNotify(tags, booru_name, widget);
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

// 태그를 카테고리별로 나누는 함수 //////////////////////////////////////////////////////////////////////
let tag_category;
let tag_category2;
let tags_by_category = {
	"general" : [],
	"artist" : [],
	"copyright" : [],
	"character" : [],
	"meta" : []
}
let category_priority;

function categorizeValue(widget) {

	function parsePromptAttention(text) {
		const attnSyntax = /\\\(|\\\)|\\\[|\\]|\\\\|\\|\(|\[|:\s*([+-]?[\d.]+)\s*\)|\)|\]|[^\\()[\]:]+|:/g;
		const reBreak = /\s*\bBREAK\b\s*/g;

		const result = [];
		const roundBrackets = [];
		const squareBrackets = [];

		const roundBracketMultiplier = 1.1;
		const squareBracketMultiplier = 1 / 1.1;

		function multiplyRange(start, multiplier) {
			for (let i = start; i < result.length; i++) {
				result[i][1] *= multiplier;
			}
		}

		let match;
		while ((match = attnSyntax.exec(text)) !== null) {
			const token = match[0];
			const weight = match[1];

			if (token.startsWith("\\")) {
				result.push([token.slice(1), 1.0]);
			} else if (token === "(") {
				roundBrackets.push(result.length);
			} else if (token === "[") {
				squareBrackets.push(result.length);
			} else if (weight !== undefined && roundBrackets.length > 0) {
				multiplyRange(roundBrackets.pop(), parseFloat(weight));
			} else if (token === ")" && roundBrackets.length > 0) {
				multiplyRange(roundBrackets.pop(), roundBracketMultiplier);
			} else if (token === "]" && squareBrackets.length > 0) {
				multiplyRange(squareBrackets.pop(), squareBracketMultiplier);
			} else {
				const parts = token.split(reBreak);
				for (let i = 0; i < parts.length; i++) {
					if (i > 0) {
						result.push(["BREAK", -1]);
					}
					result.push([parts[i], 1.0]);
				}
			}
		}

		for (const pos of roundBrackets) {
			multiplyRange(pos, roundBracketMultiplier);
		}

		for (const pos of squareBrackets) {
			multiplyRange(pos, squareBracketMultiplier);
		}

		if (result.length === 0) {
			result.push(["", 1.0]);
		}

		// Merge consecutive entries with same weight
		let i = 0;
		while (i + 1 < result.length) {
			if (result[i][1] === result[i + 1][1]) {
				result[i][0] += result[i + 1][0];
				result.splice(i + 1, 1);
			} else {
				i++;
			}
		}

		return result;
	}
	
	function removeComment(input) {
	  return input
		// 블록 주석 제거 (/* ... */)
		.replace(/\/\*[\s\S]*?\*\//g, '')
		// 줄별로 나눈 후
		.split('\n')
		.map(line => {
		  // 라인 주석 제거 (// 또는 # 이후 부분 제거)
		  return line.replace(/\/\/.*$/g, '').replace(/#.*$/g, '');
		})
	}
	
	function parseTagWeightArray(inputArray) {
	  return inputArray.flatMap(([tags, weight]) => {
		// 소수점 세 자리로 반올림
		const roundedWeight = Math.round(weight * 1000) / 1000;
		  
		if (typeof tags === 'string') {
		  return tags
			.split(',')
			.map(tag => tag.trim())
			.filter(tag => tag.length > 0) // 빈 문자열 제거
			.map(tag => [tag, roundedWeight]);
		} else {
		  return [[tags, roundedWeight]];
		}
	  });
	}
	
	function categorizeTags(inputTagsWithWeight, categoryMaps, priorityList) {
	  const result = {};

		// 태그가 속한 가장 높은 우선순위의 카테고리를 찾는 함수
		function getTopCategory(tag, categoryMaps) {
		  for (const map of categoryMaps) {
			let categories = map[tag] || [];

			// 특수 조건에 따른 카테고리 재정의			
			/* if ((categories.includes("gender") || categories.includes("girl")) && tag.includes("girl")) {
			  categories = ["female"];
			} else if (tag.endsWith("_girl")) {
			  categories = ["female"];
			} else if (categories.includes("gender") && tag.includes("boy")) {
			  categories = ["male"];
			} else if (tag.endsWith("_boy")) {
			  categories = ["male"];
			} else if (tag.endsWith("_focus")) {
			  categories = ["camera"];
			} else if (categories.includes("hair_style") || categories.includes("hair_color")) {
			  categories = ["hair"];
			} else if (categories.includes("eye") || categories.includes("eyes") || categories.includes("face") || tag.endsWith("_ears")) {
			  categories = ["face"];
			} else if (tag.endsWith("hat") || categories.includes("hat")) {
			  categories = ["headwear"];
			} else if (categories.includes("expression") || categories.includes("emotion")) {
			  categories = ["expression & emotion"];
			} else if (categories.includes("accessory") || categories.includes("hair_accessory") || categories.includes("jewelry") || tag.endsWith("_earring") || tag.endsWith("halo") || tag.endsWith("_ornament")) {
			  categories = ["accessory"];
			} else if (categories.includes("armor") || tag.endsWith("_clothes") || tag.endsWith("_shorts")|| tag.endsWith("_shoes")|| tag.endsWith("_boots")) {
			  categories = ["clothing"];
			} else if (categories.includes("body_modification") || tag.endsWith("_wings") || tag.endsWith("_tail")) {
			  categories.unshift("body");
			} else if (tag.includes("pubic_hair") || categories.includes("sensitive")) {
			  categories = ["sensitive"];
			} else if (categories.includes("pose") || categories.includes("action") || categories.includes("touch") || categories.includes("touching") || tag.startsWith("holding_")) {
			  categories = ["pose & action"];
			} else if (categories.includes("relationship")) {
			  categories = ["person"];
			} else if (categories.includes("people")) {
			  categories.unshift("person");
			} else if (categories.includes("props") || categories.includes("item") || tag.startsWith("unworn_")) {
			  categories = ["object"];
			} else if (tag.includes("place") || categories.includes("location")) {
			  categories = ["place & location"];
			} else if (categories.includes("architecture")) {
			  categories.unshift("background");
			} */
			
			if (Array.isArray(categories) && categories.length > 0) {
			  // 우선순위 기준으로 정렬
			  const sorted = [...categories].sort((a, b) => {
				const ai = priorityList.indexOf(a);
				const bi = priorityList.indexOf(b);
				return (ai === -1 ? Infinity : ai) - (bi === -1 ? Infinity : bi);
			  });

			  return sorted[0];
			}
		  }

		  return null;
		}

	  // 사전 정의된 메타 정보로부터 카테고리를 찾는 함수
	  function findTagFromCategory(tag) {
		for (const category of ["meta", "copyright", "character", "artist"]) {
		  if (tags_by_category[category]?.includes(tag)) {
			return category;
		  }
		}
		return null;
	  }

	  // 결과 객체에 카테고리 배열이 없으면 생성 후 반환
	  const getOrCreateCategoryArray = (category) => {
		if (!result[category]) result[category] = [];
		return result[category];
	  };

	  // 입력된 태그들을 순회하며 적절한 카테고리에 분류
	  inputTagsWithWeight.forEach(([tag, weight]) => {
		const topCategory = getTopCategory(tag, categoryMaps);

		if (topCategory) {
		  getOrCreateCategoryArray(topCategory).push([tag, weight]);
		} else {
		  const fallbackCategory = findTagFromCategory(tag) || "*unclassified*";
		  getOrCreateCategoryArray(fallbackCategory).push([tag, weight]);
		}
	  });

	  return result;
	}
	
	function writeSortedCategorizedTags(categorizedTags, category_priority) {
	  const categoryArray = Object.keys(category_priority);
	  const sortedEntries = Object.entries(categorizedTags).sort(([a], [b]) => {
		if (a === "*unclassified*") return 1; // *unclassified*는 항상 뒤로
		if (b === "*unclassified*") return -1;

		const indexA = categoryArray.indexOf(a);
		const indexB = categoryArray.indexOf(b);

		const inA = indexA !== -1;
		const inB = indexB !== -1;

		if (inA && inB) return indexA - indexB;
		if (inA) return -1;
		if (inB) return 1;
		return a.localeCompare(b); // 우선순위에 없는 항목은 알파벳 순
	  });
	  
	  let outputText = "";
	  const localeSetting = app.ui.settings.getSettingValue("Comfy.Locale");
	  sortedEntries.forEach(([category, tags]) => {
		if (localeSetting === "ko") category = (category_priority[category]) ? category_priority[category] : category;
		category = (category === "artist") ? "artist:" : category;
		outputText += `//${category}` + "\n";

		const formattedTags = tags.map(([tag, weight]) => {
		  // 괄호 이스케이프 처리
		  const escapedTag = tag.replace(/\(/g, "\\(").replace(/\)/g, "\\)");
		  if (weight == 1) return escapedTag;
		  else if (weight == 1.1) return `(${escapedTag})`;
		  else if (weight == 1.21) return `((${escapedTag}))`;
		  else if (weight == 1.331) return `(((${escapedTag})))`;
		  else return `(${escapedTag}:${weight})`;
		});

		outputText += formattedTags.join(", ") + ",\n\n";
	  });
	  return outputText;
	}

	if (!widget.value) return showMessage("Error", "No tags in text box");
	if (!tag_category || !category_priority) return showMessage("Error", "JSON files were not loaded");

	const tags = parseTagWeightArray(parsePromptAttention(removeComment(widget.value)));	
	const c_tag = categorizeTags(tags, [tag_category, tag_category2], category_priority);
	const result_txt = writeSortedCategorizedTags(c_tag, category_priority);
	if (result_txt) {
		widget.value = result_txt;
		showMessage("Info", "Tags have been successfully categorized.")
	}
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

function clearWidgets(node) {
	const baseWidgetMap = {
		"LoRA Stacker 💬ED": ["lora_name", "model_str", "clip_str", "lora_wt"],
		"Embedding Stacker 💬ED": ["positive_embedding", "positive_emphasis", "negative_embedding", "negative_emphasis"]
	};

	const widgetNames = baseWidgetMap[node.comfyClass];
	if (!widgetNames) return;

	for (let i = 1; i <= 9; i++) {
		for (let widgetName of widgetNames) {
			const fullName = `${widgetName}_${i}`;
			const widget = findWidgetByName(node, fullName);
			if (!widget) continue;

			if (widgetName === "lora_name" || widgetName === "positive_embedding" || widgetName === "negative_embedding") {
				widget.value = "None";
			} else {
				widget.value = 1;
			}
		}
	}
	showMessage("Info", node.comfyClass + " has been cleared.")
}


function getBooruTagRegionalScript(node) {
	const CLASS_CONFIG = {
		"Get Booru Tag 💬ED":    { tbox_id: 1, combo_id: 1, has_lora: false, has_group_tag:true},
		"Regional Script 💬ED":   { tbox_id: 4, combo_id: 4, has_lora: false, has_group_tag:false},
		"Context To DetailerPipe":{ tbox_id: 0, combo_id: 1, has_lora: true, has_group_tag:false}
	};

	function applyComboBehavior(comboWidget, tboxWidget, isWildcard = true, lora = false) {
		comboWidget.callback = (value, canvas, node, pos, e) => {
			if (isWildcard) {
				if (tboxWidget.value !== '') {
					tboxWidget.value = tboxWidget.value.replace(/,\s*$/, '') + ', ';
				}
				tboxWidget.value += node._wildcard_value + ",";
			} else if (lora) {
				let lora_name = node._value;
				if (lora_name.endsWith('.safetensors')) {
					lora_name = lora_name.slice(0, -12);
				}
				tboxWidget.value += `<lora:${lora_name}>`;
				if (node.widgets_values) {
					node.widgets_values[config.tbox_id] = tboxWidget.value;
				}
			}
		};
	}

	function defineComboValue(widget, defaultText, propName) {
		Object.defineProperty(widget, "value", {
			set: (value) => {
				if (value !== defaultText)
					node[propName] = value;
			},
			get: () => defaultText
		});
	}

	function defineComboOptions(widget, optionsGetter) {
		Object.defineProperty(widget.options, "values", {
			set: (_) => {},
			get: optionsGetter
		});
	}

	// For the first group of nodes
	if (CLASS_CONFIG[node.comfyClass]) {
		const config = CLASS_CONFIG[node.comfyClass];
		node._value = "Select the LoRA to add to the text";

		const tboxWidget = node.widgets[config.tbox_id];
		const wildcardCombo = node.widgets[config.combo_id + 1];

		// Wildcard combo behavior
		applyComboBehavior(wildcardCombo, tboxWidget, true);
		defineComboValue(wildcardCombo, "Select the Wildcard to add to the text", "_wildcard_value");
		defineComboOptions(wildcardCombo, () => wildcards_list);
		wildcardCombo.serializeValue = () => "Select the Wildcard to add to the text";

		// Optional: Group tag feature
		if (config.has_group_tag) {
			const groupCombo = node.widgets[config.combo_id + 2];
			groupCombo.callback = () => categorizeValue(tboxWidget);
			defineComboOptions(groupCombo, () => ["[Group tags by category]"]);
			defineComboValue(groupCombo, "Group tags by category", "_value");
		}

		// Optional: LoRA handling
		if (config.has_lora) {
			const loraCombo = node.widgets[config.combo_id];
			applyComboBehavior(loraCombo, tboxWidget, false, true);
			defineComboValue(loraCombo, "Select the LoRA to add to the text", "_value");
			loraCombo.serializeValue = () => "Select the LoRA to add to the text";
		}
	}

	// For Regional Stacker / Processor
	if (node.comfyClass === "Regional Stacker 💬ED" || node.comfyClass === "Regional Processor 💬ED") {
		const emptyImageWidget = node.widgets[3];
		const widthWidget = node.widgets[1];
		const heightWidget = node.widgets[2];

		emptyImageWidget.callback = () => {
			createEmptyImage(widthWidget.value, heightWidget.value);
		};

		defineComboValue(emptyImageWidget, "Create empty image", "_wildcard_value");
		defineComboOptions(emptyImageWidget, () => ["[Create empty image]"]);
		emptyImageWidget.serializeValue = () => "Create empty image";
	}
	
	// For LoRA Stacker 💬ED
	if (node.comfyClass === "LoRA Stacker 💬ED") {
		const clearLorasWidget = findWidgetByName(node, "Clear LoRAs");

		clearLorasWidget.callback = () => {
			clearWidgets(node);
		};

		defineComboValue(clearLorasWidget, "Clear LoRAs", "_wildcard_value");
		defineComboOptions(clearLorasWidget, () => ["[Clear LoRAs]"]);
		clearLorasWidget.serializeValue = () => "Clear LoRAs";
	}
	
	// For Embedding Stacker 💬ED
	if (node.comfyClass === "Embedding Stacker 💬ED") {
		const clearEmbeddingWidget = findWidgetByName(node, "Clear embeddings");

		clearEmbeddingWidget.callback = () => {
			clearWidgets(node);
		};

		defineComboValue(clearEmbeddingWidget, "Clear embeddings", "_wildcard_value");
		defineComboOptions(clearEmbeddingWidget, () => ["[Clear embeddings]"]);
		clearEmbeddingWidget.serializeValue = () => "Clear embeddings";
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
		const date = Date.now();
		tag_category = await fetchJson('./extensions/efficiency-nodes-ED/json/tag_category.json?v=' + date);
		tag_category2 = await fetchJson('./extensions/efficiency-nodes-ED/json/tag_category2.json?v=' + date);
		category_priority = await fetchJson('./extensions/efficiency-nodes-ED/json/categoryPriority.json?v=' + date);
		tags_by_category.artist = await fetchJson('./extensions/efficiency-nodes-ED/json/tags_by_category/artist.json?v=' + date);
		tags_by_category.copyright = await fetchJson('./extensions/efficiency-nodes-ED/json/tags_by_category/copyright.json?v=' + date);
		tags_by_category.character = await fetchJson('./extensions/efficiency-nodes-ED/json/tags_by_category/character.json?v=' + date);
		tags_by_category.meta = await fetchJson('./extensions/efficiency-nodes-ED/json/tags_by_category/meta.json?v=' + date);
		gelApiKey = await fetchJson('./extensions/efficiency-nodes-ED/json/gelbooruApiKey.json?v=' + date);
		
        dynamicWidgets_initialized = true;
    },
});

