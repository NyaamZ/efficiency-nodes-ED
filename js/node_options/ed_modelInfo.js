import { app } from "../../../scripts/app.js";
//import { api } from "../../../scripts/api.js";
import { $el } from "../../../scripts/ui.js";
import { ModelInfoDialog } from "../../ComfyUI-Custom-Scripts/js/common/modelInfoDialog.js";
import { LoraInfoDialog } from "../../ComfyUI-Custom-Scripts/js/modelInfo.js";
import { addMenuHandler } from "./common/utils.js";

class CheckpointInfoDialog extends ModelInfoDialog {
	async addInfo() {
		super.addInfo();
		const info = await this.addCivitaiInfo();
		if (info) {
			this.addInfoEntry("Base Model", info.baseModel || "⚠️ Unknown");

			$el("div", {
				parent: this.content,
				innerHTML: info.description,
				style: {
					maxHeight: "250px",
					overflow: "auto",
				},
			});
		}
	}
}

const generateNames = (prefix, start, end) => {
    const result = [];
    if (start < end) {
        for (let i = start; i <= end; i++) {
            result.push(`${prefix}${i}`);
        }
    } else {
        for (let i = start; i >= end; i--) {
            result.push(`${prefix}${i}`);
        }
    }
	return result
}

const generateNames2 = (prefix, second, start, end) => {
    const result = [];
    if (start < end) {
        for (let i = start; i <= end; i++) {
            result.push(`${prefix}${i}`);
        }
    } else {
        for (let i = start; i >= end; i--) {
            result.push(`${prefix}${i}`);
        }
    }
    if (start < end) {
        for (let i = start; i <= end; i++) {
            result.push(`${second}${i}`);
        }
    } else {
        for (let i = start; i >= end; i--) {
            result.push(`${second}${i}`);
        }
    }
	return result
}



// NOTE: Orders reversed so they appear in ascending order
const infoHandler = {
	"Efficient Loader 💬ED": {
        "checkpoints": ["ckpt_name"]
    },
    "Embedding Stacker 💬ED": {
		"embeddings": generateNames2("negative_embedding_", "positive_embedding_", 50, 1)
    },
	    "LoRA Stacker 💬ED": {
        "loras": generateNames("lora_name_", 50, 1)
    },
	"LoRA Stacker": {
        "loras": generateNames("lora_name_", 50, 1)
    },
};

// Utility functions and other parts of your code remain unchanged

app.registerExtension({
    name: "efficiency_ED.ed_ModelInfo",
    beforeRegisterNodeDef(nodeType) {
        const types = infoHandler[nodeType.comfyClass];

        if (types) {
            addMenuHandler(nodeType, function (_, options) {// Here, we are calling addMenuHandler
                let submenuItems = [];  // to store submenu items

                const addSubMenuOption = (type, widgetNames) => {
					const widgetreverse = [...widgetNames].reverse();
                    widgetreverse.forEach(widgetName => {
                        const widgetValue = this.widgets.find(w => w.name === widgetName)?.value;
                        
                        // Check if widgetValue is "None"
						if (widgetValue != null){
							if (widgetValue['content'] == "None") {
                            return;
							}
						}
						
                        if (!widgetValue || widgetValue === "None" || widgetValue === "(use same)") {
                            return;
                        }
                        
                        let value = widgetValue;
                        if (value.content) {
                            value = value.content;
                        }
                        const cls = type === "loras" ? LoraInfoDialog : CheckpointInfoDialog;

                        const label = widgetName; 

                        // Push to submenuItems
                        submenuItems.push({
                            content: label,
                            callback: async () => {
                                new cls(value).show(type, value);
                            },
                        });
                    });
                };

                if (typeof types === 'object') {
                    Object.keys(types).forEach(type => {
                        addSubMenuOption(type, types[type]);
                    });
                }

                // If we have submenu items, use insertOption
                if (submenuItems.length) {
                    options.unshift({ // Using insertOption here
                        content: "🔍 View model info...",
                        has_submenu: true,
                        callback: (value, options, e, menu, node) => {
                            new LiteGraph.ContextMenu(submenuItems, {
                                event: e,
                                callback: null,
                                parentMenu: menu,
                                node: node
                            });

                            return false; // This ensures the original context menu doesn't proceed
                        }
                    });
                }
            });
        }
    },
});






