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
	console.error('JSON 파일을 불러오는 중 오류 발생:', error);
  }
}


export function findWidgetByName(node, widgetName) {
    return node.widgets.find(widget => widget.name === widgetName);
}

const doesInputWithNameExist = (node, name) => {
    //return node.inputs ? node.inputs.some((input) => input.name === name) : false;
	return false;
};

export function updateNodeHeight(node) {node.setSize([node.size[0], node.computeSize()[1]]);}

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

/*     
	const GROUPED_MENU_ORDER = {
        "🔄 Swap with...": 0,
        "⛓ Add link...": 1,
        "📜 Add script...": 2,
        "🔍 View model info...": 3,
        "🌱 Seed behavior...": 4,
        "📐 Set Resolution...": 5,
        "✏️ Add 𝚇 input...": 6,
        "✏️ Add 𝚈 input...": 7
    };
	
	const originalGetOpts = nodeType.prototype.getExtraMenuOptions;

    nodeType.prototype.getExtraMenuOptions = function () {
        let r = originalGetOpts ? originalGetOpts.apply(this, arguments) || [] : [];

        const insertOption = (option) => {
            if (GROUPED_MENU_ORDER.hasOwnProperty(option.content)) {
                // Find the right position for the option
                let targetPos = r.length; // default to the end
                
                for (let i = 0; i < r.length; i++) {
                    if (GROUPED_MENU_ORDER.hasOwnProperty(r[i].content) && 
                        GROUPED_MENU_ORDER[option.content] < GROUPED_MENU_ORDER[r[i].content]) {
                        targetPos = i;
                        break;
                    }
                }
                // Insert the option at the determined position
                r.splice(targetPos, 0, option);
            } else {
                // If the option is not in the GROUPED_MENU_ORDER, simply add it to the end
                r.push(option);
            }
        };

        cb.call(this, insertOption);

        return r;
    };
	*/
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
