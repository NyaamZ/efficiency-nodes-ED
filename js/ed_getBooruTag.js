import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
// TODO: 나중에 복구 (clipspace 기능) — import { ComfyApp } from "../../scripts/app.js";

import { findWidgetByName, showMessage, fetchJson, ed_log, ed_warn, ed_error } from "./node_options/common/utils.js";

// [수정] 정적 import 는 하나만 실패해도 이 파일 전체(그리고 이 파일을 import 하는 ed_dynamicWidgets.js)가
//        로드되지 않는다. 신버전에서 사라졌을 수 있는 clipspace.js 는 동적 import + 실패 허용으로 바꿈.
// TODO: 나중에 복구 (clipspace 기능)
// let ClipspaceDialog = null;
// import("../../extensions/core/clipspace.js")
	// .then(m => { ClipspaceDialog = m.ClipspaceDialog ?? null; })
	// .catch(e => console.warn("clipspace.js 를 불러오지 못했습니다 (빈 이미지 생성 기능에만 영향)", e));

// [수정] ed_dynamicWidgets.js 와의 순환 import 제거 → findPreviousNode 는 필요한 시점에 동적 import

// 신버전에서는 nodeCreated 시점에 node.type 이 비어 있을 수 있으므로 comfyClass 를 우선 사용
const nodeClass = (n) => n?.comfyClass || n?.type || "";
const getGraphNodes = () => app.graph?._nodes ?? app.graph?.nodes ?? [];

// app.ui.settings 는 deprecated → extensionManager.setting 우선
function getLocale() {
	try {
		return app.extensionManager?.setting?.get("Comfy.Locale")
			?? app.ui?.settings?.getSettingValue("Comfy.Locale");
	} catch {
		return undefined;
	}
}

let wildcards_list = [];

async function load_wildcards() {
	try {
		let res = await api.fetchApi('/impact/wildcards/list');

		if (!res.ok) {
			ed_log(`서버 오류: ${res.status} ${res.statusText}`);
			wildcards_list = [];
			return;
		}
		let data = await res.json();
		if (!data || !data.data) {
			ed_log("응답 데이터에 'data' 필드가 없습니다.");
			wildcards_list = [];
			return;
		}
		wildcards_list = data.data;
		ed_log("와일드카드 불러오기 성공:", wildcards_list);

	} catch (err) {
		ed_log("와일드카드 불러오기 실패:", err.message);
		wildcards_list = [];
	}
}

load_wildcards();

// Get Booru Tag ED Handlers
let ed_settings = {};

export async function handleGetBooruTag(node, widget) {

	function htmlUnescape(string) {
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
		if (!tags)
			return showError('ERROR: Tags not found in JSON file.');

		if (typeof tags !== 'string')
			return showError('ERROR: Tags are not string.');

		setTags(tags);

		const capitalizedSite = capitalizeFirstLetter(booruSite);

		widget.value = widget.value.replaceAll(
			booruSite,
			capitalizedSite
		);

		showMessage(
			"Success",
			`${capitalizedSite} tags are successfully loaded`
		);
	}

	function capitalizeFirstLetter(text) {
		return text.charAt(0).toUpperCase() + text.slice(1);
	}

	// 태그 설정 함수
	function setTags(tags) {
		if (tagsWidget) {
			let tag_data = htmlUnescape(
				tags.replaceAll(' ', ', ') + ","
			);

			tagsWidget.value = tag_data;
		}
	}

	// 에러 표시
	function showError(error, showTag = false) {
		showMessage("Error", error);
	}

	// --------------------------------------------------------
	// Booru API 요청
	// --------------------------------------------------------
	async function fetchData(booru, id, api_key = "") {

		try {

			// ------------------------------------------------
			// Danbooru: 브라우저에서 직접 요청
			// ------------------------------------------------
			if (booru === "danbooru") {
				const url = `https://danbooru.donmai.us/posts/${id}.json`;

				ed_log(`Danbooru direct request: ${url}`);

				const response = await fetch(url, {
					method: "GET",
					headers: {
						"Accept": "application/json"
					}
				});

				ed_log(`Danbooru HTTP Status: ${response.status}`);

				if (!response.ok) {
					throw new Error(`Danbooru HTTP ${response.status}`);
				}

				const result = await response.json();

				ed_log("Danbooru request successful");

				return result;
			}

			// ------------------------------------------------
			// 나머지 Booru: Python 백엔드 요청
			// ------------------------------------------------
			ed_log(`Fetching from Python backend: ${booru} ID ${id}`);

			const response = await fetch(
				"/ed/booru_tags",
				{
					method: "POST",

					headers: {
						"Content-Type": "application/json"
					},

					body: JSON.stringify({
						booru: booru,
						id: id,
						api_key: api_key
					})
				}
			);

			if (!response.ok) {

				let errorMessage = `HTTP Error! Status Code: ${response.status}`;

				try {
					const errorData = await response.json();

					if (errorData.error) {
						errorMessage = errorData.error;

						if (errorData.details) {
							errorMessage += "\n" + errorData.details;
						}
					}

				} catch (e) {}

				throw new Error(errorMessage);
			}

			return await response.json();

		} catch (error) {

			showError(error.message, true);

			ed_log(`Booru API Error: ${error}`);

			return null;
		}
	}

	// --------------------------------------------------------
	// Danbooru 태그 정리
	// --------------------------------------------------------
	function getDanbooruTags(data) {

		if (!data)
			return null;

		let tags = "";

		if (data.tag_string_artist)
			tags += "/*artist*/" + data.tag_string_artist + " \n";

		if (data.tag_string_character)
			tags += "/*character*/" + data.tag_string_character + " \n";

		if (data.tag_string_copyright)
			tags += "/*copyright*/" + data.tag_string_copyright + " \n";

		tags += data.tag_string_general || "";

		return tags;
	}

	// --------------------------------------------------------
	// Booru 설정
	// --------------------------------------------------------
	const booruDict = {

		danbooru: {
			type: "danbooru",
			func: (data) => getDanbooruTags(data),
		},

		aibooru: {
			type: "danbooru",
			func: (data) => getDanbooruTags(data),
		},

		gelbooru: {
			type: "gelbooru",
			func: (data) => data?.post?.[0]?.tags,
		},

		safebooru: {
			type: "gelbooru",
			func: (data) => data?.[0]?.tags,
		},

		xbooru: {
			type: "gelbooru",
			func: (data) => data?.[0]?.tags,
		},

		konachan: {
			type: "moebooru",
			func: (data) => data?.[0]?.tags,
		},

		yande: {
			type: "moebooru",
			func: (data) => data?.[0]?.tags,
		},
	};

	// --------------------------------------------------------
	// 입력값 검사
	// --------------------------------------------------------
	if (
		!widget.value ||
		widget.value === "None" ||
		/[A-Z]/.test(widget.value.slice(0, 10))
	)
		return;

	let tagsWidget;

	if (node.comfyClass == "Get Booru Tag 💬ED")
		tagsWidget = findWidgetByName(node, "text_b");

	if (node.comfyClass == "Regional Script 💬ED")
		tagsWidget = findWidgetByName(node, "prompt");

	// --------------------------------------------------------
	// Booru 사이트 판별
	// --------------------------------------------------------
	const booru_name = Object.keys(booruDict).find(
		key => widget.value.includes(key)
	);

	if (!booru_name)
		return showError('ERROR: No matching booru found.');

	const { type, func } = booruDict[booru_name];

	let match;
	let post_id;

	// --------------------------------------------------------
	// ID 추출
	// --------------------------------------------------------
	if (type === "danbooru") {

		match = /posts\/(\d+)/.exec(widget.value);

		if (!match)
			return showError(`ERROR: ID not found in ${booru_name} URL.`);

		post_id = match[1];

	} else if (type === "gelbooru") {

		match = /id=(\d+)/.exec(widget.value);

		if (!match)
			return showError(`ERROR: ID not found in ${booru_name} URL.`);

		post_id = match[1];

	} else if (type === "moebooru") {

		match = /\/show\/(\d+)/.exec(widget.value);

		if (!match)
			return showError(`ERROR: ID not found in ${booru_name} URL.`);

		post_id = match[1];
	}

	// --------------------------------------------------------
	// Python 백엔드 요청
	// --------------------------------------------------------
	const api_key =
		booru_name === "gelbooru"
			? (ed_settings["Gelbooru_api_key"] ?? "")
			: "";

	const data = await fetchData(
		booru_name,
		post_id,
		api_key
	);

	if (!data)
		return;
	ed_log("json data :\n", data);

	// --------------------------------------------------------
	// 태그 추출
	// --------------------------------------------------------
	const tags = func(data);

	// --------------------------------------------------------
	// 위젯 업데이트
	// --------------------------------------------------------
	updateTagsAndNotify(
		tags,
		booru_name,
		widget
	);
}

// 태그를 카테고리별로 나누는 함수 //////////////////////////////////////////////////////////////////////
let tag_category;
let tag_category2;
let category_priority;
let tags_by_category = {
	"general": [],
	"artist": [],
	"copyright": [],
	"character": [],
	"meta": []
}

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

	function removeColorPrefix(tag) {
		// ComfyUI에서 흔히 쓰이는 색상 접두사 (거의 모든 기본 색상 포함)
		const colors = [
			"red_", "blue_", "green_", "yellow_", "brown_", "purple_", "pink_", "orange_",
			"gray_", "grey_", "cyan_", "lime_", "magenta_", "white_", "black_", "beige_",
			"teal_", "navy_", "maroon_", "olive_", "silver_", "gold_", "violet_", "indigo_",
			"turquoise_", "peach_", "salmon_", "chocolate_", "khaki_", "lavender_",
			"tiny_", "small_", "large_", "huge_", "gigantic_"
		];

		// 정규식으로 접두사 제거 (시작 부분)
		const regex = new RegExp(`^(${colors.join("|")})`);
		const removed = tag.replace(regex, "");
		if (tag === removed) return null;
		else return removed;
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
				// 공백을 _로 치환 & 소문자로 변환
				tag = tag.replaceAll(" ", "_").toLowerCase();
				let categories = map[tag] || [];

				if (Array.isArray(categories) && categories.length === 0) {
					const removed_tag = removeColorPrefix(tag);
					if (removed_tag) categories = map[removed_tag] || [];
				}

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
		const localeSetting = getLocale();
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

// TODO: 나중에 복구 (clipspace 기능) — createEmptyImage 전체
// async function createEmptyImage(width, height, color = "white") {

	// // 순환 import 를 피하기 위해 호출 시점에 가져온다
	// const { findPreviousNode } = await import("./ed_dynamicWidgets.js");

	// function find_script_load_image(width, height, reg_script = "Regional Script 💬ED", load_image = "LoadImage") {
		// const script_nodes = getGraphNodes().filter((n) => nodeClass(n).includes(reg_script));
		// let find_node_list = []
		// if (script_nodes.length) {
			// script_nodes.forEach((n) => {
				// find_node_list.push(findPreviousNode(n, load_image));
			// });
		// }
		// if (find_node_list.length) {
			// find_node_list.forEach((n) => {
				// if (n) ComfyApp.pasteFromClipspace(n);
			// });
		// }
		// const eff_loader = getGraphNodes().find((n) => nodeClass(n).includes("Efficient Loader 💬ED"));
		// if (eff_loader) {
			// let widget_width = findWidgetByName(eff_loader, "image_width");
			// let widget_height = findWidgetByName(eff_loader, "image_height");
			// if (widget_width) widget_width.value = width;
			// if (widget_height) widget_height.value = height;
		// }
	// }

	// async function uploadImage(filepath, formData) {
		// try {
			// await api.fetchApi('/upload/image', {
				// method: 'POST',
				// body: formData
			// });

			// const selectedIndex = ComfyApp.clipspace['selectedIndex'];
			// ComfyApp.clipspace.imgs[selectedIndex] = new Image();
			// ComfyApp.clipspace.imgs[selectedIndex].src = `view?filename=${filepath.filename}&type=${filepath.type}`;

			// if (ComfyApp.clipspace.images) {
				// ComfyApp.clipspace.images[selectedIndex] = filepath;
			// }

			// ClipspaceDialog?.invalidatePreview?.();
		// } catch (error) {
			// console.error('Error uploading image:', error);
		// }
	// }

	// // 신버전에서 Clipspace API 가 ComfyApp 에서 제거/이동됐을 가능성에 대비
	// if (typeof ComfyApp.pasteFromClipspace !== "function" || typeof ComfyApp.onClipspaceEditorSave !== "function") {
		// showMessage("Error", "이 ComfyUI 버전에서는 Clipspace API(ComfyApp.pasteFromClipspace 등)를 찾을 수 없습니다.");
		// console.error("ComfyApp clipspace API missing", Object.getOwnPropertyNames(ComfyApp).filter(k => /clipspace/i.test(k)));
		// return;
	// }

	// try {
		// // Canvas 생성 및 설정
		// const canvas = document.createElement('canvas');
		// canvas.width = width;
		// canvas.height = height;

		// const ctx = canvas.getContext("2d");
		// ctx.fillStyle = color;
		// ctx.fillRect(0, 0, width, height);

		// // Data URL 생성
		// const imageDataURL = canvas.toDataURL("image/png");

		// // Blob 생성
		// const byteString = atob(imageDataURL.split(',')[1]);
		// const byteArray = new Uint8Array(byteString.length);
		// for (let i = 0; i < byteString.length; i++) {
			// byteArray[i] = byteString.charCodeAt(i);
		// }
		// const myBlob = new Blob([byteArray], { type: 'image/png' });

		// // FormData 준비
		// const filename = "clipspace-tmp_image.png";
		// const formData = new FormData();
		// formData.append("image", new File([myBlob], filename));
		// formData.append("overwrite", "true");
		// formData.append("type", "input");

		// const item = {
			// filename,
			// subfolder: "",
			// type: "input",
		// };

		// // ComfyApp 관련 상태 업데이트
		// if (!ComfyApp.clipspace) {
			// const load_image_nodes = getGraphNodes().filter((n) => nodeClass(n).includes("Load Image") || nodeClass(n).includes("LoadImage"));
			// let found_node = false;
			// for (let n of load_image_nodes) {
				// if (n && n.imgs?.[0]) {
					// ComfyApp.copyToClipspace(n);
					// ComfyApp.clipspace_return_node = null;
					// found_node = true;
					// break;
				// }
			// }
			// if (!found_node) {
				// console.error('Unable copy Clipspace image:');
				// return;
			// }
		// }

		// if (ComfyApp.clipspace.images) {
			// ComfyApp.clipspace.images[0] = item;
		// }

		// if (ComfyApp.clipspace.widgets) {
			// const index = ComfyApp.clipspace.widgets.findIndex(obj => obj.name === 'image');
			// if (index >= 0) {
				// ComfyApp.clipspace.widgets[index].value = `${filename} [input]`;
			// }
		// }

		// // 파일 업로드 및 후속 작업
		// await uploadImage(item, formData);
		// ComfyApp.onClipspaceEditorSave();

		// find_script_load_image(width, height);
		// showMessage("Info", "Created empty image to Regional Script 💬ED")
	// } catch (error) {
		// console.error('Error saving image:', error);
	// }
// }

function clearWidgets(node) {
	const baseWidgetMap = {
		"LoRA Stacker 💬ED": ["lora_name", "model_str", "clip_str", "lora_wt"],
		"Embedding Stacker 💬ED": ["positive_embedding", "pos_weight", "negative_embedding", "neg_weight"]
	};

	const widgetNames = baseWidgetMap[node.comfyClass];
	if (!widgetNames) return;

	for (let i = 1; i <= 9; i++) {
		for (let widgetName of widgetNames) {
			const fullName = `${widgetName}_${i}`;
			const widget = findWidgetByName(node, fullName);
			if (!widget) continue;

			if (widgetName === "lora_name" || widgetName === "positive_embedding" || widgetName === "negative_embedding") {
				const toggle_widget = findWidgetByName(node, `${fullName}_toggle`);
				if (toggle_widget) toggle_widget.value = true;
				widget.value = "None";
				if (widget.isEdToggleCombo) widget.toggle = true;
			} else {
				widget.value = 1;
			}
		}
	}

	node.setDirtyCanvas(true, true);
	showMessage("Info", node.comfyClass + " has been cleared.")
}

export function getBooruTagRegionalScript_Init(node) {
    if (!node || !node.widgets) return;

    const CLASS_CONFIG = {
        "Get Booru Tag 💬ED": {
            tbox_id: 1,
            combo_id: 1,
            has_lora: false,
            has_group_tag: true
        },
        "Regional Script 💬ED": {
            tbox_id: 1,
            combo_id: 1,
            has_lora: false,
            has_group_tag: false
        },
        "Context To DetailerPipe": {
            tbox_id: 0,
            combo_id: 1,
            has_lora: true,
            has_group_tag: false
        }
    };

    function setupActionCombo(widget, {
        defaultText,
        propName,
        optionsGetter,
        onSelect
    }) {
        if (!widget) return;

        // 중복 초기화 방지
        if (widget.__edActionComboInitialized) return;
        widget.__edActionComboInitialized = true;

        // 콤보 옵션 동적 제공
        if (optionsGetter && widget.options) {
            try {
                Object.defineProperty(widget.options, "values", {
                    configurable: true,
                    enumerable: true,

                    get: optionsGetter,
                    set: function () {}
                });
            } catch (e) {
                ed_warn("options.values 설정 실패:", e);
                widget.options.values = optionsGetter;
            }
        }

        // 표시값과 저장값을 고정
        widget.value = defaultText;

        widget.serializeValue = () => defaultText;

        // 사용자 선택 이벤트
        widget.callback = function (value, canvas, currentNode, pos, event) {
            if (typeof value === "string" && value !== defaultText) {
                node[propName] = value;

                try {
                    onSelect?.(value);
                } catch (e) {
                    ed_error("combo action error:", e);
                }
            }

            // 액션 실행 후 기본 문구로 복원
            widget.value = defaultText;

            node.setDirtyCanvas?.(true, true);
        };
    }

    const widgets = node.widgets;

    // -----------------------------------------
    // Get Booru Tag / Regional Script / Context
    // -----------------------------------------
    const config = CLASS_CONFIG[node.comfyClass];

    if (config) {
        node._value = "Select the LoRA to add to the text";

        const tboxWidget = widgets[config.tbox_id];
        const wildcardCombo = widgets[config.combo_id + 1];

        if (tboxWidget && wildcardCombo) {

            // Wildcard 선택
            setupActionCombo(wildcardCombo, {
                defaultText: "Select the Wildcard to add to the text",
                propName: "_wildcard_value",
                optionsGetter: () => wildcards_list,

                onSelect: (value) => {
                    if (tboxWidget.value !== "") {
                        tboxWidget.value =
                            tboxWidget.value.replace(/,\s*$/, "") + ", ";
                    }

                    tboxWidget.value += value + ",";
                }
            });

            // Group tags
            if (config.has_group_tag) {
                setupActionCombo(widgets[config.combo_id + 2], {
                    defaultText: "Group tags by category",
                    propName: "_value",
                    optionsGetter: () => ["[Group tags by category]"],

                    onSelect: () => categorizeValue(tboxWidget)
                });
            }

            // LoRA
            if (config.has_lora) {
                setupActionCombo(widgets[config.combo_id], {
                    defaultText: "Select the LoRA to add to the text",
                    propName: "_value",

                    onSelect: (value) => {
                        let lora_name = value;

                        if (lora_name.endsWith(".safetensors")) {
                            lora_name = lora_name.slice(0, -12);
                        }

                        tboxWidget.value += `<lora:${lora_name}>`;

                        if (node.widgets_values) {
                            node.widgets_values[config.tbox_id] =
                                tboxWidget.value;
                        }
                    }
                });
            }
        }
    }

    // -----------------------------------------
    // LoRA Stacker - Clear LoRAs
    // -----------------------------------------
    if (node.comfyClass === "LoRA Stacker 💬ED") {
        setupActionCombo(findWidgetByName(node, "Clear LoRAs"), {
            defaultText: "Clear LoRAs",
            propName: "_wildcard_value",
            optionsGetter: () => ["[Clear LoRAs]"],

            onSelect: () => clearWidgets(node)
        });
    }

    // -----------------------------------------
    // Embedding Stacker - Clear embeddings
    // -----------------------------------------
    if (node.comfyClass === "Embedding Stacker 💬ED") {
        setupActionCombo(findWidgetByName(node, "Clear embeddings"), {
            defaultText: "Clear embeddings",
            propName: "_wildcard_value",
            optionsGetter: () => ["[Clear embeddings]"],

            onSelect: () => clearWidgets(node)
        });
    }
}


app.registerExtension({
	name: "ED.getBooruTag",

	async setup() {
		const date = Date.now();
		tag_category = await fetchJson('./extensions/efficiency-nodes-ED/json/tag_category.json?v=' + date);
		tag_category2 = await fetchJson('./extensions/efficiency-nodes-ED/json/tag_category2.json?v=' + date);
		category_priority = await fetchJson('./extensions/efficiency-nodes-ED/json/categoryPriority.json?v=' + date);
		tags_by_category.artist = await fetchJson('./extensions/efficiency-nodes-ED/json/tags_by_category/artist.json?v=' + date);
		tags_by_category.copyright = await fetchJson('./extensions/efficiency-nodes-ED/json/tags_by_category/copyright.json?v=' + date);
		tags_by_category.character = await fetchJson('./extensions/efficiency-nodes-ED/json/tags_by_category/character.json?v=' + date);
		tags_by_category.meta = await fetchJson('./extensions/efficiency-nodes-ED/json/tags_by_category/meta.json?v=' + date);
		ed_settings = await fetchJson('./ed_nodes/ed_settings') || {};
	},
});