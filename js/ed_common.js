import { api } from "../../scripts/api.js";

function handleTitleUpdate(node, data) {
    if (typeof node.title !== "string") {
        console.warn("node.title is not a string:", node.title);
        return;
    }

    const match = node.title.match(/\[\d+\]/);
    node.title = match ? node.title.replace(match[0], `[${data}]`) : `${node.title} [${data}]`;
}

function updateWidgetValue(node, widgetName, data) {
    if (!Array.isArray(node.widgets)) return;
    
    const widget = node.widgets.find(w => w.name === widgetName);
    if (widget) widget.value = data;
}

function nodeFeedbackHandlerEd(event) {
    const nodes = app.graph._nodes_by_id;
    const node = nodes[event.detail.node_id];

    if (!node) return;

    const { type, data, widget_name } = event.detail;

    switch (type) {
        case "log":
            console.log("ED_log:", data);
            break;
        case "sound":
            if (typeof node.playSound === "function") node.playSound();
            break;
        case "title":
            handleTitleUpdate(node, data);
            break;
        case "text":
            updateWidgetValue(node, widget_name, data);
            break;
        default:
            console.warn("Unknown event type:", type);
    }
}

api.addEventListener("ed-node-feedback", nodeFeedbackHandlerEd);
