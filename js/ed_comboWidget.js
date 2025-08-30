import { app } from "../../scripts/app.js";
import { toggleWidget, findWidgetByName, hexToRGB, darkenHex } from "./node_options/common/utils.js";
import { RgthreeModelInfoDialog, MODEL_INFO_SERVICE } from "./rgthree_util/dialog_info.js";
import { rgthreeApi } from "./rgthree_util/rgthree_api.js";

export const ED_COMBO_NODES = {
    "Efficient Loader 💬ED": "checkpoints",
    "LoRA Stacker 💬ED": "loras",
    "Embedding Stacker 💬ED": "embeddings",
};

export const COMBO_WIDGET_NAMES = {
    checkpoints: "ckpt_name",
    loras: "lora_name",
    embeddings: "embedding_",
};

async function showLoraChooser(event, modelType, callback, parentMenu, modelList) {
    var _a, _b;
    const canvas = app.canvas;
    if (modelType === "loras") {
        if (!modelList) {
            modelList = ["None", ...(await rgthreeApi.getLoras().then((modelList) => modelList.map((l) => l.file)))];
        }
    } else if (modelType === "checkpoints") {
        if (!modelList) {
            modelList = ["🔌 ext model input", ...(await rgthreeApi.getCheckpoints().then((modelList) => modelList.map((l) => l.file)))];
        }
    } else if (modelType === "embeddings") {
        if (!modelList) {
            modelList = ["None", ...(await rgthreeApi.getEmbeddings().then((modelList) => modelList.map((l) => l.file)))];
        }
    }

    new LiteGraph.ContextMenu(modelList, {
        event: event,
        parentMenu: parentMenu != null ? parentMenu : undefined,
        scale: Math.max(1, (_b = (_a = canvas.ds) === null || _a === void 0 ? void 0 : _a.scale) !== null && _b !== void 0 ? _b : 1),
        className: "dark",
        callback,
    });
}

function drawInfoIcon(ctx, widget, x, y, size = 12) {
    ctx.save();
    ctx.beginPath();
    ctx.roundRect(x, y, size, size, [size * 0.1]);

    ctx.fillStyle = darkenHex(widget.text_color, 6); //"#DDD" > "#d7d7d7", "#2f82ec";
    //widget.disabledTextColor:"#666" "#0f2a5e";
    ctx.strokeStyle = hexToRGB(widget.text_color).r > 150 ? "#0f2a5e" : widget.disabledTextColor;
    ctx.fill();
    ctx.strokeStyle = darkenHex(widget.background_color, 1); //"#222" > "#212121",  "#FFF";

    ctx.lineWidth = 2;
    const midX = x + size / 2;
    const serifSize = size * 0.175;
    ctx.stroke(new Path2D(`
    M ${midX} ${y + size * 0.15}
    v 2
    M ${midX - serifSize} ${y + size * 0.45}
    h ${serifSize}
    v ${size * 0.325}
    h ${serifSize}
    h -${serifSize * 2}
  `));
    ctx.restore();
}

function drawRoundedRectangle(ctx, options) {
    const lowQuality = isLowQuality();
    options = { ...options };
    ctx.save();
    ctx.strokeStyle = options.colorStroke || LiteGraph.WIDGET_OUTLINE_COLOR;
    ctx.fillStyle = options.colorBackground || LiteGraph.WIDGET_BGCOLOR;
    ctx.beginPath();
    ctx.roundRect(...options.pos, ...options.size, lowQuality ? [0] : options.borderRadius ? [options.borderRadius] : [options.size[1] * 0.5]);
    ctx.fill();
    !lowQuality && ctx.stroke();
    ctx.restore();
}

function drawTogglePart(ctx, options) {
    const lowQuality = isLowQuality();
    ctx.save();
    const { posX, posY, height, value } = options;
    const toggleRadius = height * 0.36;
    const toggleBgWidth = height * 1.5;
    if (!lowQuality) {
        ctx.beginPath();
        ctx.roundRect(posX + 4, posY + 4, toggleBgWidth - 8, height - 8, [height * 0.5]);
        ctx.globalAlpha = app.canvas.editor_alpha * 0.25;
        ctx.fillStyle = "rgba(255,255,255,0.45)";
        ctx.fill();
        ctx.globalAlpha = app.canvas.editor_alpha;
    }
    ctx.fillStyle = value === true ? "#89B" : "#888";
    const toggleX = lowQuality || value === false
        ? posX + height * 0.5
        : value === true
            ? posX + height
            : posX + height * 0.75;
    ctx.beginPath();
    ctx.arc(toggleX, posY + height * 0.5, toggleRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    return [posX, toggleBgWidth];
}

function fitString(ctx, str, maxWidth) {
    function binarySearch(max, getValue, match) {
        let min = 0;
        while (min <= max) {
            let guess = Math.floor((min + max) / 2);
            const compareVal = getValue(guess);
            if (compareVal === match)
                return guess;
            if (compareVal < match)
                min = guess + 1;
            else
                max = guess - 1;
        }
        return max;
    }

    function measureText(ctx, str) {
        return ctx.measureText(str).width;
    }

    let width = ctx.measureText(str).width;
    const ellipsis = "…";
    const ellipsisWidth = measureText(ctx, ellipsis);
    if (width <= maxWidth || width <= ellipsisWidth) {
        return str;
    }
    const index = binarySearch(str.length, (guess) => measureText(ctx, str.substring(0, guess)), maxWidth - ellipsisWidth);
    return str.substring(0, index) + ellipsis;
}

function isLowQuality() {
    var _a;
    const canvas = app.canvas;
    return (((_a = canvas.ds) === null || _a === void 0 ? void 0 : _a.scale) || 1) <= 0.5;
}

export class RgthBaseWidget {
    value;
    node;
    name;
    options;
    label;
    type;
    y = 0;
    last_y;
    width;
    disabled;
    computedDisabled;
    hidden;
    advanced;
    tooltip;
    element;

    constructor(widget, node) {
        this.node = node ?? widget.node;
        this.value = widget.value;
        this.name = widget.name;
        this.label = widget.label;
        this.options = widget.options;

        this.background_color = widget.background_color;
        this.disabledTextColor = widget.disabledTextColor;
        this.displayName = widget.displayName;
        this.labelBaseline = widget.labelBaseline;
        this.outline_color = widget.outline_color;
        this.secondary_text_color = widget.secondary_text_color;
        this.text_color = widget.text_color;

        this.type = "custom";
        this.y = 0;
        this.last_y = 0;
        this.mouseDowned = null;
        this.isMouseDownedAndOver = false;
        this.hitAreas = {};
        this.downedHitAreasForMove = [];
        this.downedHitAreasForClick = [];
    }
    serializeValue(node, index) {
        return this.value;
    }
    clickWasWithinBounds(pos, bounds) {
        let xStart = bounds[0];
        let xEnd = xStart + (bounds.length > 2 ? bounds[2] : bounds[1]);
        const clickedX = pos[0] >= xStart && pos[0] <= xEnd;
        if (bounds.length === 2) {
            return clickedX;
        }
        return clickedX && pos[1] >= bounds[1] && pos[1] <= bounds[1] + bounds[3];
    }
    mouse(event, pos, node) {
        var _a, _b, _c;
        const canvas = app.canvas;
        if (event.type == "pointerdown") {
            this.mouseDowned = [...pos];
            this.isMouseDownedAndOver = true;
            this.downedHitAreasForMove.length = 0;
            this.downedHitAreasForClick.length = 0;
            let anyHandled = false;
            for (const part of Object.values(this.hitAreas)) {
                if (this.clickWasWithinBounds(pos, part.bounds)) {
                    if (part.onMove) {
                        this.downedHitAreasForMove.push(part);
                    }
                    if (part.onClick) {
                        this.downedHitAreasForClick.push(part);
                    }
                    if (part.onDown) {
                        const thisHandled = part.onDown.apply(this, [event, pos, node, part]);
                        anyHandled = anyHandled || thisHandled == true;
                    }
                    part.wasMouseClickedAndIsOver = true;
                }
            }
            return (_a = this.onMouseDown(event, pos, node)) !== null && _a !== void 0 ? _a : anyHandled;
        }
        if (event.type == "pointerup") {
            if (!this.mouseDowned)
                return true;
            this.downedHitAreasForMove.length = 0;
            const wasMouseDownedAndOver = this.isMouseDownedAndOver;
            this.cancelMouseDown();
            let anyHandled = false;
            for (const part of Object.values(this.hitAreas)) {
                if (part.onUp && this.clickWasWithinBounds(pos, part.bounds)) {
                    const thisHandled = part.onUp.apply(this, [event, pos, node, part]);
                    anyHandled = anyHandled || thisHandled == true;
                }
                part.wasMouseClickedAndIsOver = false;
            }
            for (const part of this.downedHitAreasForClick) {
                if (this.clickWasWithinBounds(pos, part.bounds)) {
                    const thisHandled = part.onClick.apply(this, [event, pos, node, part]);
                    anyHandled = anyHandled || thisHandled == true;
                }
            }
            this.downedHitAreasForClick.length = 0;
            if (wasMouseDownedAndOver) {
                const thisHandled = this.onMouseClick(event, pos, node);
                anyHandled = anyHandled || thisHandled == true;
            }
            return (_b = this.onMouseUp(event, pos, node)) !== null && _b !== void 0 ? _b : anyHandled;
        }
        if (event.type == "pointermove") {
            this.isMouseDownedAndOver = !!this.mouseDowned;
            if (this.mouseDowned &&
                (pos[0] < 15 ||
                    pos[0] > node.size[0] - 15 ||
                    pos[1] < this.last_y ||
                    pos[1] > this.last_y + LiteGraph.NODE_WIDGET_HEIGHT)) {
                this.isMouseDownedAndOver = false;
            }
            for (const part of Object.values(this.hitAreas)) {
                if (this.downedHitAreasForMove.includes(part)) {
                    part.onMove.apply(this, [event, pos, node, part]);
                }
                if (this.downedHitAreasForClick.includes(part)) {
                    part.wasMouseClickedAndIsOver = this.clickWasWithinBounds(pos, part.bounds);
                }
            }
            return (_c = this.onMouseMove(event, pos, node)) !== null && _c !== void 0 ? _c : true;
        }
        return false;
    }
    cancelMouseDown() {
        this.mouseDowned = null;
        this.isMouseDownedAndOver = false;
        this.downedHitAreasForMove.length = 0;
    }
    onMouseDown(event, pos, node) {
        return;
    }
    onMouseUp(event, pos, node) {
        return;
    }
    onMouseClick(event, pos, node) {
        return;
    }
    onMouseMove(event, pos, node) {
        return;
    }
}

export class EdToggleComboWidget extends RgthBaseWidget {
    toggle = true;
    constructor(widget, node, modelType) {
        super(widget, node);
        this.haveMouseMovedStrength = false;
        this.loraInfoPromise = null;
        this.loraInfo = null;
        this.modelType = modelType;
        this.hitAreas = {
            toggle: { bounds: [0, 0], onDown: this.onToggleDown },
            lora: { bounds: [0, 0], onClick: this.onLoraClick },
            info: { bounds: [0, 0], onClick: this.onInfoDown },
        };
        if (this.modelType === "checkpoints") {
            delete this.hitAreas.toggle;
        }
    }
    setInitToggle() {
        const indexOffset = 37;
        const num = Number(this.name.replace(/\D/g, ""));
        let widgetValue;

        switch (this.modelType) {
            case "checkpoints":
                this.toggle = true;
                break;

            case "loras":
                widgetValue = this.node.widgets_values[indexOffset + num];
                this.toggle = widgetValue ?? true; // null 또는 undefined이면 true
                break;

            case "embeddings":
                if (this.name.includes("pos")) {
                    widgetValue = this.node.widgets_values[indexOffset + num];
                } else {
                    widgetValue = this.node.widgets_values[indexOffset + 9 + num];
                }
                this.toggle = widgetValue ?? true;
                break;

            default:
                this.toggle = true;
                break;
        }
    }
    draw(ctx, node, w, posY, height) {
        var _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o, _p;
        ctx.save();
        const margin = 15;
        const leftPadding = 10;
        const innerMargin = margin * 0.33;
        const lowQuality = isLowQuality();
        const midY = posY + height * 0.5;
        let posX = margin;
        drawRoundedRectangle(ctx, { pos: [posX, posY], size: [node.size[0] - margin * 2, height] });

        posX += leftPadding;
        ctx.fillStyle = "#999";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        const w_name = this.replaceName();
        const nameWidth = ctx.measureText(w_name).width
        if (this.modelType === "checkpoints") {
            posX += 8;
        }
        ctx.fillText(fitString(ctx, w_name, nameWidth), posX, midY);
        posX += nameWidth + innerMargin;

        if (this.modelType != "checkpoints") {
            this.hitAreas.toggle.bounds = drawTogglePart(ctx, { posX, posY, height, value: this.toggle });
            posX += this.hitAreas.toggle.bounds[1] + innerMargin;
        }

        if (lowQuality) {
            ctx.restore();
            return;
        }
        if (!this.toggle) {
            ctx.globalAlpha = app.canvas.editor_alpha * 0.4;
        }
        ctx.fillStyle = LiteGraph.WIDGET_TEXT_COLOR;
        let rposX = node.size[0] - margin - 2; // - innerMargin;
        //let textColor = "#c66";

        const infoIconSize = height * 0.66;
        const infoWidth = infoIconSize + innerMargin + innerMargin;

        rposX -= innerMargin;
        if (this.value != "None" && this.value != "🔌 ext model input") {
            drawInfoIcon(ctx, this, rposX - infoIconSize + 1, posY + (height - infoIconSize) / 2, infoIconSize);
            this.hitAreas.info.bounds = [rposX - infoIconSize, infoWidth];
        }
        rposX = rposX - infoIconSize - margin;

        const loraWidth = rposX - posX;
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        ctx.fillText(fitString(ctx, this.value, loraWidth), rposX, midY);
        this.hitAreas.lora.bounds = [posX, loraWidth];
        posX += loraWidth + innerMargin;
        ctx.globalAlpha = app.canvas.editor_alpha;
        ctx.restore();
    }
    replaceName() {
        if (this.name.includes("lora_name")) {
            return this.name.replace("lora_name", "lora");
        }
        if (this.name.includes("positive_embedding_")) {
            return this.name.replace("positive_embedding_", "pos_emb_");
        }
        if (this.name.includes("negative_embedding_")) {
            return this.name.replace("negative_embedding_", "neg_emb_");
        }
        return this.name;
    }
    onToggleDown(event, pos, node) {
        this.toggle = !this.toggle;
        this.cancelMouseDown();
        const w = findWidgetByName(node, this.name + "_toggle");
        if (w) w.value = this.toggle;
        return true;
    }
    onInfoDown(event, pos, node) {
        this.showLoraInfoDialog();
    }
    onLoraClick(event, pos, node) {
        showLoraChooser(event, this.modelType, (value) => {
            if (typeof value === "string") {
                this.value = value;
                this.loraInfo = null;
                this.getLoraInfo();
            }
            node.setDirtyCanvas(true, true);
        });
        this.cancelMouseDown();
    }
    onMouseUp(event, pos, node) {
        super.onMouseUp(event, pos, node);
        this.haveMouseMovedStrength = false;
    }
    showLoraInfoDialog() {
        if (!this.value || this.value === "None") {
            return;
        }
        const infoDialog = new RgthreeModelInfoDialog(this.value, this.modelType).show();
        infoDialog.addEventListener("close", ((e) => {
            if (e.detail.dirty) {
                this.getLoraInfo(true);
            }
        }));
    }
    getLoraInfo(force = false) {
        if (!this.loraInfoPromise || force == true) {
            let promise;
            if (this.value && this.value != "None") {
                promise = MODEL_INFO_SERVICE(this.modelType).getInfo(this.value, force, true);
            }
            else {
                promise = Promise.resolve(null);
            }
            this.loraInfoPromise = promise.then((v) => (this.loraInfo = v));
        }
        return this.loraInfoPromise;
    }
}

export function edComboWidget_Init(node) {
    if (!ED_COMBO_NODES[node.comfyClass]) {
        return;
    }

    for (let i = 0; i < node.widgets.length; i++) {
        const w = node.widgets[i];
        if (w.name.includes("toggle")) {
            toggleWidget(node, w, false);
        }
        else if (w.name.includes(COMBO_WIDGET_NAMES[ED_COMBO_NODES[node.comfyClass]]) && w.constructor.name != "EdToggleComboWidget") {
            node.widgets[i] = new EdToggleComboWidget(w, node, ED_COMBO_NODES[node.comfyClass]);
        }
    }
}



/* 
app.registerExtension({
    name: "ED.test",
    nodeCreated(node) {
        if (!node || !ED_COMBO_NODES[node.comfyClass]) {
            return;				
        }		

        if (node.widgets) {
            for (let i = 0; i < node.widgets.length; i++) {
                const w = node.widgets[i];
                if (w.name.includes("toggle")) {
                    toggleWidget(node, w, false);
                }				
                else if (w.name.includes(COMBO_WIDGET_NAMES[ED_COMBO_NODES[node.comfyClass]])) {
                    node.widgets[i] = new EdToggleComboWidget(w, node, ED_COMBO_NODES[node.comfyClass]);
                }
            }
        }
    },
    afterConfigureGraph() {
        const filteredNodes = app.graph._nodes.filter(node => ED_COMBO_NODES.hasOwnProperty(node.comfyClass));

        filteredNodes.forEach(node => {
            node.widgets.forEach(widget => {
                if (widget.constructor.name === "EdToggleComboWidget") {
                    widget.setInitToggle();
                }
            });
        });
    },
});
 */