import { app } from "../../scripts/app.js";

import { toggleWidget, findWidgetByName, updateNodeHeight, flashWidget, RESIZE_ALLOWED_NODES, ed_dlog, ed_dwarn, ed_error } from "./node_options/common/utils.js";

import { edComboWidget_Init, ED_COMBO_NODES } from "./ed_comboWidget.js"

let dynamicWidgets_initialized = false;
ed_dlog("① 모듈 로드됨 (import 성공) — ed_dynamicWidgets.js");

// [진단/안정화] 아래 두 파일은 정적 import 가 아니라 동적 import 로 불러온다.
//  - 정적 import 는 하나만 실패해도 이 파일 전체가 조용히 로드되지 않는다.
//  - 동적 import 는 실패해도 이 파일은 정상 로드되고, 콘솔에 "실제 에러 원인"이 출력된다.
let handleGetBooruTag = null;
let getBooruTagRegionalScript_Init = null;
let edAppearance_Init = null;

try {
    ({ edAppearance_Init } = await import("./ed_appearance.js"));
    ed_dlog("ed_appearance.js 로드 성공");
} catch (e) {
    ed_error("[ED] ed_appearance.js 로드 실패 →", e);
}

try {
    ({ handleGetBooruTag, getBooruTagRegionalScript_Init } = await import("./ed_getBooruTag.js"));
    ed_dlog("ed_getBooruTag.js 로드 성공");
} catch (e) {
    ed_error("[ED] ed_getBooruTag.js 로드 실패 →", e);
}

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
        'url': handleGetBooruTag
    },
    "Get Booru Tag 💬ED": {
        'url': handleGetBooruTag
    },
};

/////////////////////////////////////////////////////////////////////////// ED

// ----------------------
// 호환성 헬퍼 (신버전 프론트엔드 대응)
// ----------------------

// 위젯 토글 (위젯이 없으면 조용히 무시)
function safeToggle(node, widget, ...args) {
    if (!widget) {
        ed_dwarn("safeToggle: 위젯을 못 찾음 (node:", node?.comfyClass, ")");
        return;
    }
    toggleWidget(node, widget, ...args);
    ed_dlog(`toggle → ${widget.name} show=${args[0]} | hidden=${widget.hidden} type=${widget.type} class=${widget.constructor?.name}`);
}

// combo 위젯의 options.values 는 배열이 아니라 함수일 수 있음
function getComboValues(widget) {
    const v = widget?.options?.values;
    if (typeof v === "function") {
        try { return v(widget) ?? []; } catch { return []; }
    }
    return Array.isArray(v) ? v : [];
}

// 신버전: graph.links 가 Map / Proxy 일 수 있고, 서브그래프에서는 node.graph 가 app.graph 와 다름
function getLink(graph, linkId) {
    if (!graph || linkId == null) return null;
    if (typeof graph.getLink === "function") {
        const l = graph.getLink(linkId);
        if (l) return l;
    }
    const links = graph.links;
    if (!links) return null;
    if (links instanceof Map) return links.get(linkId) ?? null;
    return links[linkId] ?? null;
}

function getNodeFromLink(node, linkId, from = "") {
    const graph = node.graph ?? app.graph;
    const linkInfo = getLink(graph, linkId) ?? getLink(app.graph, linkId);
    if (!linkInfo) return null;
    const id = from === "origin" ? linkInfo.origin_id : linkInfo.target_id;
    return graph.getNodeById(id);
}

function isMatchingNode(node, nodeType) {
    // 신버전: nodeCreated 시점에는 node.type 이 비어 있을 수 있어 comfyClass 우선
    return (node.comfyClass || node.type)?.includes(nodeType);
}

export function findPreviousNode(node, targetType) {
    if (!node) return null;

    for (const port of (node.inputs ?? [])) {
        const link = port.link;
        if (link == null) continue;

        const connectedNode = getNodeFromLink(node, link, "origin");
        if (!connectedNode) continue;

        if (isMatchingNode(connectedNode, targetType)) {
            return connectedNode;
        }
    }
    return null;
}


function recursive_FindLinkedNode(node, nodeType) {

    function isContextNode(node) {
        const t = node.comfyClass || node.type;
        return t && (t.includes('Context') || t === 'Wildcard Encode 💬ED' || t === 'TIPO Script 💬ED');
    }

    if (!node) return null;
    const links = node.outputs?.[0]?.links;
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

// input_mode 에 따른 위젯 표시/숨김
function handleInputModeWidgetsVisibility(node, inputModeValue) {
    function generateWidgetNames(baseName, count) {
        return Array.from({ length: count }, (_, i) => `${baseName}_${i + 1}`);
    }

    const loraWtWidgets = [...generateWidgetNames("lora_wt", 10)];
    const modelStrWidgets = [...generateWidgetNames("model_str", 10)];
    const clipStrWidgets = [...generateWidgetNames("clip_str", 10)];

    const nodeVisibilityMap = {
        "LoRA Stacker 💬ED": {
            "simple": [...modelStrWidgets, ...clipStrWidgets],
            "advanced": [...loraWtWidgets]
        },
    };

    const inputModeVisibilityMap = nodeVisibilityMap[node.comfyClass];

    if (!inputModeVisibilityMap || !inputModeVisibilityMap[inputModeValue]) return;

    // 전부 보이게 초기화
    for (const key in inputModeVisibilityMap) {
        for (const widgetName of inputModeVisibilityMap[key]) {
            safeToggle(node, findWidgetByName(node, widgetName), true);
        }
    }

    // 현재 모드에서 숨길 위젯
    for (const widgetName of inputModeVisibilityMap[inputModeValue]) {
        safeToggle(node, findWidgetByName(node, widgetName), false);
    }
}

// Handle multi-widget visibilities
function handleVisibility(node, widget, node_type) {
    const baseNamesMap = {
        "LoRA Stacker 💬ED": ["lora_name", "model_str", "clip_str", "lora_wt"],
        "Embedding Stacker 💬ED_pos": ["positive_embedding", "pos_weight"],
        "Embedding Stacker 💬ED_neg": ["negative_embedding", "neg_weight"]
    };
    const initValue = {
        "lora_name": "None",
        "model_str": 1,
        "clip_str": 1,
        "lora_wt": 1,
        "positive_embedding": "None",
        "pos_weight": 1,
        "negative_embedding": "None",
        "neg_weight": 1
    };

    function initWidgetVar(w) {
        if (!w) return;
        const matchedKey = Object.keys(initValue).find(key => w.name.includes(key));
        if (matchedKey) {
            w.value = initValue[matchedKey];
        }
    }

    const countValue = widget?.value;
    const baseNames = baseNamesMap[node_type];
    if (!baseNames || countValue == null) return;

    const isLora = node_type === "LoRA Stacker 💬ED";

    for (let i = 1; i <= 9; i++) {
        const widget_1 = findWidgetByName(node, `${baseNames[0]}_${i}`);
        const widget_2 = findWidgetByName(node, `${baseNames[1]}_${i}`);
        const widget_3 = isLora ? findWidgetByName(node, `${baseNames[2]}_${i}`) : null;
        const widget_4 = isLora ? findWidgetByName(node, `${baseNames[3]}_${i}`) : null;

        if (i <= countValue) {

            if (isLora) {
                const inputModeValue = findWidgetByName(node, "input_mode")?.value;

                safeToggle(node, widget_1, true);
                if (inputModeValue === "simple") {
                    safeToggle(node, widget_2, false);  // model_str
                    safeToggle(node, widget_3, false);  // clip_str
                    safeToggle(node, widget_4, true);   // lora_wt
                } else if (inputModeValue === "advanced") {
                    safeToggle(node, widget_2, true);   // model_str
                    safeToggle(node, widget_3, true);   // clip_str
                    safeToggle(node, widget_4, false);  // lora_wt
                }
            } else if (node_type.includes("Embedding Stacker 💬ED")) {
                safeToggle(node, widget_1, true);   // _embedding
                safeToggle(node, widget_2, true);   // _weight
            }
        }
        else {
            safeToggle(node, widget_1, false);
            if (widget_1?.isEdToggleCombo) widget_1.toggle = true;
            initWidgetVar(widget_1);
            safeToggle(node, widget_2, false);
            initWidgetVar(widget_2);
            if (widget_3) {
                safeToggle(node, widget_3, false);
                initWidgetVar(widget_3);
            }
            if (widget_4) {
                safeToggle(node, widget_4, false);
                initWidgetVar(widget_4);
            }
            const toggle_widget = findWidgetByName(node, `${baseNames[0]}_${i}_toggle`);
            if (toggle_widget) toggle_widget.value = true;
        }
    }
}

function widgetLogic(node, widget) {
    const handler = NODE_WIDGET_HANDLERS[node.comfyClass]?.[widget.name];
    if (!handler) ed_dwarn(`widgetLogic: 핸들러 없음 ${node.comfyClass} / ${widget.name}`);
    if (handler) {
        ed_dlog(`④ 핸들러 실행: ${node.comfyClass} / ${widget.name} = ${widget.value} → ${handler.name}`);
        try {
            const r = handler(node, widget);
            if (r && typeof r.catch === "function") {
                r.catch(e => ed_error(`[ED.DynamicWidgets] async handler error: ${node.comfyClass} / ${widget.name}`, e));
            }
        } catch (e) {
            ed_error(`[ED.DynamicWidgets] handler error: ${node.comfyClass} / ${widget.name}`, e);
        }
    }
}

// Efficient Loader ED Paint Mode Handlers
function handleEfficientLoaderPaintMode_ED(node, widget) {
    const sampler_ed = recursive_FindLinkedNode(node, 'KSampler (Efficient) 💬ED')

    if (!sampler_ed?.toggleWidgetByProperty) return;

    const target_widget = findWidgetByName(sampler_ed, "denoise");
    let flashWidget_list = [];

    if (widget.value == '✍️ Txt2Img') {
        PREV_value.denoise = backupAndSet(target_widget, 1.0, flashWidget_list);
        sampler_ed.toggleWidgetByProperty(false);
    } else if (widget.value == '🎨 Inpaint(MaskDetailer)') {
        PREV_value.denoise = restoreIfMatch(target_widget, 1.0, PREV_value.denoise, flashWidget_list);
        sampler_ed.toggleWidgetByProperty(true);
    }
    else {
        PREV_value.denoise = restoreIfMatch(target_widget, 1.0, PREV_value.denoise, flashWidget_list);
        sampler_ed.toggleWidgetByProperty(false);
    }
    flashWidget(node, flashWidget_list);
}

let PREV_value = {
    denoise: 0.8,
    sdxl:  { vae: null, clipSkip: null, cfg: null, sampler: null, scheduler: null },
    flux:  { vae: null, clipSkip: null, cfg: null, sampler: null, scheduler: null },
    anima: { vae: null, clipSkip: null, cfg: null, sampler: null, scheduler: null },
};

// ----------------------
// Helper Functions
// ----------------------

// 값을 새로운 값으로 덮어쓰고, 기존 값을 반환 (백업용)
function backupAndSet(widget, newValue, flashWidgetList = [], prevValue = null) {
    if (!widget) return prevValue;

    if (prevValue != null) {
        if (widget.value != prevValue) {
            widget.value = prevValue;
            flashWidgetList.push(widget);
        }
        return prevValue;
    }

    if (newValue === undefined) return widget.value;     // 설정할 값을 못 찾은 경우
    if (widget.value === newValue) return widget.value;  // 변화 없음
    const oldVal = widget.value;
    widget.value = newValue;
    flashWidgetList.push(widget);
    return oldVal;
}

// widget.value가 특정 값과 같을 때만 이전 값으로 되돌림
function restoreIfMatch(widget, matchValue, prevValue, flashWidgetList = []) {
    if (!widget) return prevValue;
    if (widget.value === matchValue && widget.value != prevValue) {
        widget.value = prevValue;
        flashWidgetList.push(widget);
    }
    return prevValue;
}

function findVaeAndSave(wVae, wClipSkip, wCfg, wSampler, wScheduler) {
    if (!wVae) return;

    let prevType;
    if (wVae.value === "🔌 ext model input") {
        prevType = PREV_value.flux;
    } else if (contains(wVae.value, "anima") || contains(wVae.value, "qwen")) {
        prevType = PREV_value.anima;
    } else {
        prevType = PREV_value.sdxl;
    }

    prevType.vae = wVae.value;
    prevType.clipSkip = wClipSkip?.value;
    prevType.cfg = wCfg?.value;
    prevType.sampler = wSampler?.value;
    prevType.scheduler = wScheduler?.value;
}

// 텍스트에 특정 키워드 포함 여부 확인
function contains(text, keyword) {
    return typeof text === "string" && text.toLowerCase().includes(keyword);
}

// ----------------------
// Main Handler
// ----------------------
function handleEfficientLoaderFluxMode_ED(node, widget) {

    function changeStackerMode(node, mode = 0) {
        const loraStacker = findPreviousNode(node, "LoRA Stacker 💬ED");
        if (loraStacker) {
            loraStacker.mode = mode;

            const embeddingStacker = findPreviousNode(loraStacker, "Embedding Stacker 💬ED");
            if (embeddingStacker) {
                embeddingStacker.mode = mode;
            }
        }
    }

    if (!dynamicWidgets_initialized) return;

    const wClipSkip = findWidgetByName(node, "clip_skip");
    const wCfg = findWidgetByName(node, "cfg");
    const wVae = findWidgetByName(node, "vae_name");
    const wSampler = findWidgetByName(node, "sampler_name");
    const wScheduler = findWidgetByName(node, "scheduler");

    if (!wVae) return;

    const vaeValues = getComboValues(wVae);
    const fluxVae = vaeValues.find(v => contains(v, "flux"));
    const sdxlVae = vaeValues.find(v => contains(v, "sdxl_vae"));
    const animaVae = vaeValues.find(v => contains(v, "anima") || contains(v, "qwen"));

    const ckptValue = String(widget.value ?? "");
    let flashWidgetList = [];

    if (ckptValue === "🔌 ext model input") {
        // Flux 모드
        findVaeAndSave(wVae, wClipSkip, wCfg, wSampler, wScheduler);

        PREV_value.flux.vae = backupAndSet(wVae, fluxVae, flashWidgetList, PREV_value.flux.vae);
        PREV_value.flux.clipSkip = backupAndSet(wClipSkip, 0, flashWidgetList, PREV_value.flux.clipSkip);
        PREV_value.flux.cfg = backupAndSet(wCfg, 1, flashWidgetList, PREV_value.flux.cfg);
        PREV_value.flux.sampler = backupAndSet(wSampler, "euler", flashWidgetList, PREV_value.flux.sampler);
        PREV_value.flux.scheduler = backupAndSet(wScheduler, "normal", flashWidgetList, PREV_value.flux.scheduler);

        changeStackerMode(node, 4);

    } else if (ckptValue.includes("Anima")) {
        // Anima 모드
        findVaeAndSave(wVae, wClipSkip, wCfg, wSampler, wScheduler);

        PREV_value.anima.vae = backupAndSet(wVae, animaVae, flashWidgetList, PREV_value.anima.vae);
        PREV_value.anima.clipSkip = backupAndSet(wClipSkip, 0, flashWidgetList, PREV_value.anima.clipSkip);
        PREV_value.anima.cfg = backupAndSet(wCfg, 5, flashWidgetList, PREV_value.anima.cfg);
        PREV_value.anima.sampler = backupAndSet(wSampler, "er_sde", flashWidgetList, PREV_value.anima.sampler);
        PREV_value.anima.scheduler = backupAndSet(wScheduler, "simple", flashWidgetList, PREV_value.anima.scheduler);

        changeStackerMode(node, 0);

    } else {
        // 일반 모델 모드
        findVaeAndSave(wVae, wClipSkip, wCfg, wSampler, wScheduler);

        PREV_value.sdxl.vae = backupAndSet(wVae, sdxlVae, flashWidgetList, PREV_value.sdxl.vae);
        PREV_value.sdxl.clipSkip = backupAndSet(wClipSkip, -2, flashWidgetList, PREV_value.sdxl.clipSkip);
        PREV_value.sdxl.cfg = backupAndSet(wCfg, 5, flashWidgetList, PREV_value.sdxl.cfg);
        PREV_value.sdxl.sampler = backupAndSet(wSampler, "euler_ancestral", flashWidgetList, PREV_value.sdxl.sampler);
        PREV_value.sdxl.scheduler = backupAndSet(wScheduler, "normal", flashWidgetList, PREV_value.sdxl.scheduler);

        changeStackerMode(node, 0);
    }

    // 위젯 깜빡임 효과
    flashWidget(node, flashWidgetList);
}

// Sampler Set Seed ED Handlers
function handleEfficientSamplerSetSeed_ED(node, widget) {
    const opened = !(widget.value === "from context");

    safeToggle(node, findWidgetByName(node, 'seed'), opened);
    safeToggle(node, findWidgetByName(node, 'control_after_generate'), opened);
    safeToggle(node, findWidgetByName(node, 'cfg'), opened);
    safeToggle(node, findWidgetByName(node, 'sampler_name'), opened);
    safeToggle(node, findWidgetByName(node, 'scheduler'), opened);

    node.setDirtyCanvas(true, true);
}

// LoadImage ED Handlers
function handleLoadImage_ED(node, widget) {
    const opened = !(String(widget.value ?? "").includes("not upscale"));

    safeToggle(node, findWidgetByName(node, 'width'), opened);
    safeToggle(node, findWidgetByName(node, 'height'), opened);
    safeToggle(node, findWidgetByName(node, 'keep_proportions'), opened);
}

// UltimateSDUpscaler ED Handlers
function handleUltimateSDUpscalerTileSize_ED(node, widget) {
    if (widget.value == 'Image size' || widget.value == 'Canvas size') {
        safeToggle(node, findWidgetByName(node, 'tile_width'));
        safeToggle(node, findWidgetByName(node, 'tile_height'));
    } else {
        safeToggle(node, findWidgetByName(node, 'tile_width'), true);
        safeToggle(node, findWidgetByName(node, 'tile_height'), true);
    }
}

// LoRA Stacker ED Handlers
function handleLoRAStackerEDInputMode(node, widget) {
    handleInputModeWidgetsVisibility(node, widget.value);
    handleVisibility(node, findWidgetByName(node, "lora_count"), "LoRA Stacker 💬ED");
    updateNodeHeight(node);
    node.setDirtyCanvas(true, true);
}

function handleLoRAStackerEDLoraCount(node, widget) {
    handleVisibility(node, widget, "LoRA Stacker 💬ED");
    updateNodeHeight(node);
    node.setDirtyCanvas(true, true);
}

// Embedding Stacker ED Handlers
function handleEmbeddingStacker(node, widget) {
    const posORneg = widget.name.substr(0, 3);
    handleVisibility(node, widget, "Embedding Stacker 💬ED_" + posORneg);
    updateNodeHeight(node);
    node.setDirtyCanvas(true, true);
}

// ----------------------
// 위젯 변경 감지
// ----------------------
// 신버전 프론트엔드는 노드가 그래프에 추가된 "이후"에 위젯의 value getter/setter 를 다시 설정합니다.
// (rgthree 가 'Overrides value getter before widget getter is prepared' 로 차단한 것과 같은 문제)
// 그래서 nodeCreated 시점에 value 를 defineProperty 로 가로채면 나중에 덮어써져서 핸들러가 영영 호출되지 않습니다.
//  - 기본 위젯: widget.callback 을 감싸서 사용자 조작 시 핸들러 호출
//  - 그래프 로드: afterConfigureGraph 에서 한 번 더 일괄 적용 (refreshWidgetLogic)
//  - EdToggleComboWidget(직접 만든 일반 클래스): 기존처럼 value 프로퍼티 후킹 (프론트엔드가 건드리지 않음)
function hookWidgetChange(node, w) {
    if (w.__edChangeHooked) return;
    w.__edChangeHooked = true;

    ed_dlog(`② 후킹: ${node.comfyClass} / ${w.name} | typeof callback=${typeof w.callback} | class=${w.constructor?.name} | isEdToggleCombo=${!!w.isEdToggleCombo}`);

    // 1.59 대의 프론트엔드: 위젯 값은 Pinia 스토어에 있고 value 는 접근자로 관리됩니다.
    // value 를 직접 가로채지 않고, 값 변경 시 호출되는 callback 만 감쌉니다.
    // (EdToggleComboWidget 은 ed_comboWidget.js 의 onLoraClick 에서 callback 을 직접 호출)
    const origCallback = w.callback;
    w.callback = function (...args) {
        ed_dlog(`③ callback 호출됨: ${node.comfyClass} / ${w.name} = ${w.value}`);
        const r = origCallback?.apply(this, args);
        widgetLogic(node, w);
        return r;
    };
}

function applyWidgetLogic_Init(node) {
    const handlers = NODE_WIDGET_HANDLERS[node.comfyClass];
    if (!handlers || !node.widgets) {
        if (/ED|Stacker/.test(String(node.comfyClass ?? node.type))) {
            ed_dwarn(`applyWidgetLogic_Init 건너뜀: comfyClass="${node.comfyClass}" type="${node.type}" handlers=${!!handlers} widgets=${!!node.widgets}`);
        }
        return;
    }

    ed_dlog(`applyWidgetLogic_Init: ${node.comfyClass} | 위젯 목록 =`, node.widgets.map(w => w.name).join(", "));

    for (const w of [...node.widgets]) {
        if (!handlers[w.name]) continue;

        widgetLogic(node, w);
        hookWidgetChange(node, w);
    }
}

// 값을 바꾸거나 네트워크 요청을 하는 핸들러는 일괄 적용에서 제외 (표시/숨김 전용 핸들러만 재적용)
const SWEEP_SKIP = new Set([
    handleEfficientLoaderPaintMode_ED,
    handleEfficientLoaderFluxMode_ED,
    handleGetBooruTag,
]);

function refreshWidgetLogic(node) {
    const handlers = NODE_WIDGET_HANDLERS[node.comfyClass];
    if (!handlers || !node.widgets) return;

    // 현재 노드 크기 백업
    const originalSize = node.size ? [...node.size] : null;

    for (const w of [...node.widgets]) {
        const h = handlers[w.name];
        if (!h || SWEEP_SKIP.has(h)) continue;

        widgetLogic(node, w);
    }

    // 핸들러가 변경한 노드 크기를 원래 크기로 복원
    if ( !(RESIZE_ALLOWED_NODES.includes(node.comfyClass)) && originalSize && node.setSize) {
        node.setSize(originalSize);
    }

    node.setDirtyCanvas?.(true, true);
}

function safeInit(name, fn, node) {
    if (typeof fn !== "function") return;   // 해당 파일 로드에 실패한 경우 건너뜀
    try {
        fn(node);
        if (name === "edComboWidget_Init" && ED_COMBO_NODES[node?.comfyClass]) {
            ed_dlog(`edComboWidget_Init 완료: ${node.comfyClass} | 위젯 클래스 =`, node.widgets?.map(w => `${w.name}:${w.constructor?.name}`).join(", "));
        }
    } catch (e) {
        ed_error(`[ED.DynamicWidgets] ${name} failed on ${node?.comfyClass}`, e);
    }
}

app.registerExtension({
    name: "ED.DynamicWidgets",

    async setup() {
        ed_dlog("⓪ 확장 setup() 호출됨 — registerExtension 성공");
    },

    async beforeConfigureGraph() {
        dynamicWidgets_initialized = false;
    },

    nodeCreated(node) {
        if (/ED|Stacker/.test(String(node.comfyClass ?? node.type))) {
            ed_dlog(`nodeCreated: comfyClass="${node.comfyClass}" type="${node.type}" | 핸들러 등록 여부=${!!NODE_WIDGET_HANDLERS[node.comfyClass]}`);
        }
        // 하나가 실패해도 나머지가 계속 동작하도록 개별 보호
        safeInit("edAppearance_Init", edAppearance_Init, node);
        safeInit("edComboWidget_Init", edComboWidget_Init, node);
        safeInit("getBooruTagRegionalScript_Init", getBooruTagRegionalScript_Init, node);
        safeInit("applyWidgetLogic_Init", applyWidgetLogic_Init, node);

        // 노드가 그래프에 추가되고 프론트엔드의 위젯 준비가 끝난 뒤 한 번 더 적용
        setTimeout(() => safeInit("refreshWidgetLogic", refreshWidgetLogic, node), 0);
    },

    async afterConfigureGraph() {
        const allNodes = app.graph?._nodes ?? app.graph?.nodes ?? [];
        // 로드 후 위젯이 BaseWidget 으로 변환/교체됐는지 확인
        allNodes.filter(n => ED_COMBO_NODES[n.comfyClass]).forEach(n => {
            ed_dlog(`⑥-a ${n.comfyClass} 위젯 상태:`, (n.widgets ?? []).filter(w => /lora_name|ckpt_name|embedding/.test(w.name)).map(w => `${w.name}[${w.constructor?.name}, isEd=${!!w.isEdToggleCombo}, hasDraw=${typeof w.draw}]`).join(", "));
        });
        ed_dlog(`⑥ afterConfigureGraph: 노드 ${allNodes.length}개, ED 핸들러 대상 ${allNodes.filter(n => NODE_WIDGET_HANDLERS[n.comfyClass]).length}개`);
        const filteredNodes = allNodes.filter(node => ED_COMBO_NODES.hasOwnProperty(node.comfyClass));
        filteredNodes.forEach(node => {
            node.widgets?.forEach(widget => {
                if (widget.isEdToggleCombo && typeof widget.setInitToggle === "function") {
                    widget.setInitToggle();
                }
            });
        });

        // 로드된 값 기준으로 표시/숨김 일괄 재적용
        allNodes.forEach(node => safeInit("refreshWidgetLogic", refreshWidgetLogic, node));

        setTimeout(() => {
            dynamicWidgets_initialized = true;
        }, 1000);
    },
});