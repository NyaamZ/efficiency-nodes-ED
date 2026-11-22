import { app } from '../../../../scripts/app.js'
import { $el } from "../../../../scripts/ui.js";

const LOG = false;     // 진단 로그 (로드/생성/후킹 등). 확인이 끝나면 false 로
export const ed_log = (...a) => { console.log("%c[ED]", "color:#4af;font-weight:bold", ...a); };
export const ed_dlog = (...a) => { if (LOG) console.log("%c[ED]", "color:#4af;font-weight:bold", ...a); };
export const ed_warn = (...a) => { console.warn("%c[ED]", "color:#4af;font-weight:bold", ...a); };
export const ed_dwarn = (...a) => { if (LOG) console.warn("%c[ED]", "color:#4af;font-weight:bold", ...a); };
export const ed_error = (...a) => { console.error("%c[ED]", "color:#4af;font-weight:bold", ...a); };

export async function fetchJson(fileAddress) {
    try {
        const response = await fetch(fileAddress);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(fileAddress + 'JSON 파일을 불러오는 중 오류 발생:', error);
        return null;
    }
}


export function findWidgetByName(node, widgetName) {
    return node.widgets.find(widget => widget.name === widgetName);
}

const doesInputWithNameExist = (node, name) => {
    //return node.inputs ? node.inputs.some((input) => input.name === name) : false;
    return false;
};

export function updateNodeHeight(node) { node.setSize([node.size[0], node.computeSize()[1]]); }

// 위젯 인스턴스별 원본 속성 저장
const origProps = new WeakMap();

// 노드 크기 갱신을 허용할 노드 목록
export const RESIZE_ALLOWED_NODES = [
    "FaceDetailer 💬ED",
    "MaskDetailer 💬ED",
    "Detailer (SEGS) 💬ED",
    "Embedding Stacker 💬ED",
    "Ultimate SD Upscale 💬ED",
    "LoRA Stacker 💬ED",
    "SUPIR Sampler 💬ED",
    "Refiner Script 💬ED",
];

export function toggleWidget(node, widget, show = false, suffix = "") {
    if (!node || !widget) return;

    if (doesInputWithNameExist(node, widget.name)) return;

    // 원본 속성 저장 (최초 1회)
    let original = origProps.get(widget);
    if (!original) {
        original = {
            type: widget.type,
            hadOwnComputeSize: Object.prototype.hasOwnProperty.call(widget, "computeSize"),
            computeSize: widget.computeSize,
        };
        origProps.set(widget, original);
    }

    if (show) {
        // 신버전: hidden 플래그
        widget.hidden = false;
        if (widget.options) widget.options.hidden = false;

        // 구버전 호환: type / computeSize 복원
        widget.type = original.type;

        if (original.hadOwnComputeSize) {
            widget.computeSize = original.computeSize;
        } else {
            delete widget.computeSize;
        }
    } else {
        // 신버전: hidden 플래그
        widget.hidden = true;
        if (widget.options) widget.options.hidden = true;

        // 구버전 호환
        widget.type = "hidden";
        widget.computeSize = () => [0, -4];
    }

    // 연결된 위젯도 동일하게 처리
    if (Array.isArray(widget.linkedWidgets)) {
        for (const linkedWidget of widget.linkedWidgets) {
            toggleWidget(node, linkedWidget, show, suffix);
        }
    }

    // 배열에 등록된 노드만 크기 갱신
    if (
        RESIZE_ALLOWED_NODES.includes(node.comfyClass) &&
        node.computeSize &&
        node.setSize
    ) {
        const computed = node.computeSize();

        if (computed && Number.isFinite(computed[1])) {
            node.setSize([node.size[0], computed[1]]);
        }
    }

    node.setDirtyCanvas?.(true, true);
}

export function showMessage(short_msg, detail_msg) {
    try {
        app.extensionManager.toast.add({
            severity: short_msg.toLowerCase(),
            summary: short_msg,
            detail: detail_msg,
            life: 3500
        });
    }
    catch {
        // do nothing
    }
}


export function addStylesheet(url) {
    if (url.endsWith(".js")) {
        url = url.substr(0, url.length - 2) + "css";
    }
    $el("link", {
        parent: document.head,
        rel: "stylesheet",
        type: "text/css",
        href: url.startsWith("http") ? url : getUrl(url),
    });
}

export function getUrl(path, baseUrl) {
    if (baseUrl) {
        return new URL(path, baseUrl).toString();
    } else {
        return new URL("../" + path, import.meta.url).toString();
    }
}

export async function loadImage(url) {
    return new Promise((res, rej) => {
        const img = new Image();
        img.onload = res;
        img.onerror = rej;
        img.src = url;
    });
}

export function addMenuHandler(nodeType, cb) {

    const getOpts = nodeType.prototype.getExtraMenuOptions;
    nodeType.prototype.getExtraMenuOptions = function () {
        const r = getOpts.apply(this, arguments);
        cb.apply(this, arguments);
        return r;
    };
}

// Utility functions
export function addNode(name, nextTo, options) {
    options = { select: true, shiftX: 0, shiftY: 0, before: false, ...(options || {}) };
    const node = LiteGraph.createNode(name);
    app.graph.add(node);
    node.pos = [
        nextTo.pos[0] + options.shiftX,
        nextTo.pos[1] + options.shiftY,
    ];
    if (options.select) {
        app.canvas.selectNode(node, false);
    }
    return node;
}

////////////////////////////////////////////////////////////////////////// COLOR////////////////////////////////////////////////////////////////////////////
export const hexToRGB = hex => {
    // #RGB → #RRGGBB 확장
    if (hex.length === 4) {
        hex =
            "#" +
            hex[1] + hex[1] +
            hex[2] + hex[2] +
            hex[3] + hex[3];
    }

    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);

    return { r, g, b };
};

export const rgbToHex = ({ r, g, b }, shorten = true) => {
    const hex =
        "#" +
        r.toString(16).padStart(2, "0") +
        g.toString(16).padStart(2, "0") +
        b.toString(16).padStart(2, "0");

    if (shorten) {
        if (hex[1] === hex[2] && hex[3] === hex[4] && hex[5] === hex[6]) {
            return "#" + hex[1] + hex[3] + hex[5];
        }
    }

    return hex;
};

export function darkenHex(hex, amount = 6) {
    const { r, g, b } = hexToRGB(hex);

    const newR = Math.max(0, r - amount);
    const newG = Math.max(0, g - amount);
    const newB = Math.max(0, b - amount);

    return rgbToHex({ r: newR, g: newG, b: newB });
}


// HEX → HSL 객체
const hexToHSL = h => {
    h = h.replace(/^#/, '');
    h = h.length < 6 ? [...h].map(c => c + c).join`` : h;
    let r = parseInt(h.slice(0, 2), 16) / 255,
        g = parseInt(h.slice(2, 4), 16) / 255,
        b = parseInt(h.slice(4, 6), 16) / 255,
        m = Math.max(r, g, b),
        n = Math.min(r, g, b),
        l = (m + n) / 2,
        s = 0, H = 0;
    if (m !== n) {
        let d = m - n;
        s = l > 0.5 ? d / (2 - m - n) : d / (m + n);
        H = m === r ? (g - b) / d + (g < b ? 6 : 0) : m === g ? (b - r) / d + 2 : (r - g) / d + 4;
        H *= 60;
    }
    return { h: H, s: s * 100, l: l * 100 };
}

// HSL 객체 → HEX
const hslToHex = ({ h, s, l }) => {
    s /= 100; l /= 100;
    const k = n => (n + h / 30) % 12,
        a = s * Math.min(l, 1 - l),
        f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1))),
        toH = x => x.toString(16).padStart(2, '0');
    return `#${toH(Math.round(f(0) * 255))}${toH(Math.round(f(8) * 255))}${toH(Math.round(f(4) * 255))}`;
}

function overrideBackground_color(widget) {
    // 우리가 만든 오버라이드가 이미 있으면 그대로 사용
    if (widget._bgOverridden) return;

    // 원본 descriptor 보관 (복원용)
    widget._origBgDesc = Object.getOwnPropertyDescriptor(widget, "background_color");
    widget._background_color = widget.background_color; // getter가 있으면 현재 값 읽힘

    Object.defineProperty(widget, "background_color", {
        get() {
            return this._background_color;
        },
        set(value) {
            this._background_color = value;
        },
        configurable: true,
        enumerable: false,
    });
    widget._bgOverridden = true;
}

function restoreBackground_color(widget) {
    if (!widget._bgOverridden) return;

    if (widget._origBgDesc) {
        // 원래 own getter로 복귀
        Object.defineProperty(widget, "background_color", widget._origBgDesc);
    } else {
        // 원래 own 프로퍼티가 없었다면 제거 → 프로토타입 값 사용
        delete widget.background_color;
    }
    delete widget._origBgDesc;
    delete widget._background_color;
    widget._bgOverridden = false;
}

export function flashWidget(node, widgets, maxL = 50, duration = 2000, delay = 300) {
    if (!Array.isArray(widgets) || widgets.length === 0) return;

    const orig_bg_list = [];
    const minHSLList = [];

    widgets.forEach((widget) => {
        overrideBackground_color(widget);
        // flash가 중복 실행 중이면 이미 변한 색이 아니라 처음 원본 색을 써야 함
        if (widget._flashOrigColor === undefined) {
            widget._flashOrigColor = widget._origBgDesc?.get
                ? widget._origBgDesc.get.call(widget)
                : widget.background_color;
        }
        orig_bg_list.push(widget._flashOrigColor);
        minHSLList.push(hexToHSL(widget._flashOrigColor));
    });

    const hslList = minHSLList.map((hsl) => ({ ...hsl }));
    const start = performance.now();
    const token = Symbol();
    widgets.forEach((w) => (w._flashToken = token));

    function easeInOutExpo(t) {
        if (t === 0) return 0;
        if (t === 1) return 1;
        return t < 0.5
            ? Math.pow(2, 20 * t - 10) / 2
            : (2 - Math.pow(2, -20 * t + 10)) / 2;
    }

    const finished = new Set();

    function step(time) {
        let allDone = true;

        widgets.forEach((widget, i) => {
            if (finished.has(i)) return;

            // 다른 flash가 이 위젯을 인계받았으면 이 애니메이션은 종료
            if (widget._flashToken !== token) {
                finished.add(i);
                return;
            }

            const t = (time - start - i * delay) / duration;

            if (t < 0) {
                allDone = false;
                return;
            }

            if (t >= 1) {
                restoreBackground_color(widget);
                delete widget._flashOrigColor;
                finished.add(i);
                return;
            }

            allDone = false;

            if (t <= 0.5) {
                const eased = easeInOutExpo(t * 2);
                hslList[i].l = minHSLList[i].l + (maxL - minHSLList[i].l) * eased;
            } else {
                const eased = easeInOutExpo((t - 0.5) * 2);
                hslList[i].l = maxL - (maxL - minHSLList[i].l) * eased;
            }

            widget.background_color = hslToHex(hslList[i]);
        });

        node.setDirtyCanvas(true, true);

        if (!allDone) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
}

