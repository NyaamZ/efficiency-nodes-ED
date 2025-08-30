import { app } from '../../../../scripts/app.js'
import { $el } from "../../../../scripts/ui.js";

let origProps = {};

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

export function toggleWidget(node, widget, show = false, suffix = "") {
    if (!widget || doesInputWithNameExist(node, widget.name)) return;

    // Store the original properties of the widget if not already stored
    if (!origProps[widget.name]) {
        origProps[widget.name] = { origType: widget.type, origComputeSize: widget.computeSize };
    }

    const origSize = node.size;

    // Set the widget type and computeSize based on the show flag
    widget.type = show ? origProps[widget.name].origType : "tschide" + suffix;
    widget.computeSize = show ? origProps[widget.name].origComputeSize : () => [0, -4];

    // Recursively handle linked widgets if they exist
    widget.linkedWidgets?.forEach(w => toggleWidget(node, w, ":" + widget.name, show));

    // Calculate the new height for the node based on its computeSize method
    const height = show ? Math.max(node.computeSize()[1], origSize[1]) : node.size[1];
    node.setSize([node.size[0], height]);
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
    // 이미 오버라이드 되어 있는지 확인
    const desc = Object.getOwnPropertyDescriptor(widget, "background_color");
    if (desc && (desc.get || desc.set)) {
        return; // 이미 오버라이드 된 경우
    }

    widget._background_color = widget.background_color;

    Object.defineProperty(widget, "background_color", {
        get() {
            return this._background_color;
        },
        set(value) {
            this._background_color = value;
        },
        configurable: true,
    });
}

export function flashWidget(node, widgets, maxL = 50, duration = 2000, delay = 300) {
    if (!Array.isArray(widgets) || widgets.length === 0) return;

    const orig_bg_list = [];
    const minHSLList = [];

    widgets.forEach((widget) => {
        overrideBackground_color(widget);
        orig_bg_list.push(widget.background_color);
        minHSLList.push(hexToHSL(widget.background_color));
    });

    // 각 위젯마다 현재 HSL값 복사
    const hslList = minHSLList.map((hsl) => ({ ...hsl }));
    const start = performance.now();

    // easing 함수
    function easeInOutExpo(t) {
        if (t === 0) return 0;
        if (t === 1) return 1;
        return t < 0.5
            ? Math.pow(2, 20 * t - 10) / 2
            : (2 - Math.pow(2, -20 * t + 10)) / 2;
    }

    function step(time) {
        let allDone = true;

        widgets.forEach((widget, i) => {
            const delayTime = i * delay;
            const elapsed = time - start - delayTime;
            let t = elapsed / duration;

            if (t < 0) {
                allDone = false; // 아직 시작 전
                return;
            }

            if (t >= 1) {
                // 원래 색으로 복원
                widget.background_color = orig_bg_list[i];
                return;
            }

            allDone = false; // 아직 애니메이션 진행 중

            let eased;
            if (t <= 0.5) {
                eased = easeInOutExpo(t * 2);
                hslList[i].l = minHSLList[i].l + (maxL - minHSLList[i].l) * eased;
            } else {
                eased = easeInOutExpo((t - 0.5) * 2);
                hslList[i].l = maxL - (maxL - minHSLList[i].l) * eased;
            }

            widget.background_color = hslToHex(hslList[i]);
        });

        node.setDirtyCanvas(true, true);

        if (!allDone) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}

/* 
function easeInOutQuad(t) {
    return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
}
// easeInOutQuart easing 함수
function easeInOutQuart(t) {
    return t < 0.5
        ? 8 * t * t * t * t
        : 1 - Math.pow(-2 * t + 2, 4) / 2;
}

// easeInOutExpo easing 함수
function easeInOutExpo(t) {
    if (t === 0) return 0;
    if (t === 1) return 1;
    return t < 0.5
        ? Math.pow(2, 20 * t - 10) / 2
        : (2 - Math.pow(2, -20 * t + 10)) / 2;
}
 */