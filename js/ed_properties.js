import {app} from "../../scripts/app.js";
import {ComfyWidgets} from "../../scripts/widgets.js";
import { applyTextReplacements } from "../../scripts/utils.js";

import { toggleWidget, findWidgetByName } from "./ed_widgethider.js";

// Set Property
app.registerExtension({
    name: "ed.efficientLoaderED",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "Efficient Loader 💬ED") { //|| nodeData.name === "Eff. Loader SDXL 💬ED") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated?.apply(this, arguments);
				
				this.setProperty("Use tiled VAE encode", false);
				this.setProperty("Synchronize widget with image size", true);
				this.setProperty("Token normalization", "none")
				this.constructor["@Token normalization"] = {
					type: "combo",
					values: ["none", "mean", "length", "length+mean"],
				};
				this.setProperty("Weight interpretation", "comfy")
				this.constructor["@Weight interpretation"] = {
					type: "combo",
					values: ["comfy", "A1111", "compel", "comfy++", "down_weight"],
				};
				//this.setProperty("Tiled VAE encode tile size", 512);
				/* this.setProperty("Kohya-block number", 3)
				this.setProperty("Kohya-downscale factor", 2.000)
				this.setProperty("Kohya-start percent", 0.000)
				this.setProperty("Kohya-end percent", 0.350 )
				this.setProperty("Kohya-downscale after skip", true)
				this.constructor["@Kohya-downscale after skip"] = { type: "boolean" };
				this.setProperty("Kohya-downscale method", "bilinear")
				this.constructor["@Kohya-downscale method"] = {
					type: "combo",
					values: ["bicubic", "nearest-exact", "bilinear", "area", "bislerp"],
				};
				this.setProperty("Kohya-upscale method", "bilinear")
				this.constructor["@Kohya-upscale method"] = {
					type: "combo",
					values: ["bicubic", "nearest-exact", "bilinear", "area", "bislerp"],
				}; */
                return result;
            };
        }
    },
});

app.registerExtension({
    name: "ed.applyLoraED",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "Apply LoRA Stack 💬ED") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated?.apply(this, arguments);
				this.setProperty("Turn on Apply Lora", false);
                return result;
            };
        }
    },
});

app.registerExtension({
    name: "ed.KSamplerED",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "KSampler (Efficient) 💬ED") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated?.apply(this, arguments);
				this.setProperty("MaskDetailer mode", false);
				this.setProperty("(MaskDetailer) drop size", 5);
				this.setProperty("(MaskDetailer) inpaint model enable", false);
				this.setProperty("(MaskDetailer) noise mask feather", 20);
				this.setProperty("Use tiled VAE decode", false);
				
				this.toggleWidgetByProperty = (value) => {
					const adjustment  = this.size[1];
					this.properties["MaskDetailer mode"] = value;
					
					toggleWidget(this, findWidgetByName(this, 'preview_method'), !value);
					toggleWidget(this, findWidgetByName(this, 'guide_size'), value);
					toggleWidget(this, findWidgetByName(this, 'guide_size_for'), value);
					toggleWidget(this, findWidgetByName(this, 'max_size'), value);
					toggleWidget(this, findWidgetByName(this, 'feather'), value);
					toggleWidget(this, findWidgetByName(this, 'crop_factor'), value);
					toggleWidget(this, findWidgetByName(this, 'cycle'), value);
					
					if (this.size[1] < adjustment)
						this.setSize([this.size[0], adjustment]);
				};
				
				this.onPropertyChanged = (property, value) => {
					//onPropertyChanged.call(this, property, value);					
					if (property == "MaskDetailer mode"){						
						this.toggleWidgetByProperty(value);
					}
				};
				
				this.toggleWidgetByProperty(this.properties["MaskDetailer mode"]);
				
                return result;
            };
        }
    },
});

// Use widget values and dates in output filenames For SaveImage ED
app.registerExtension({
	name: "Comfy.SaveImageED_Output",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "Save Image 🔔ED") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			// When the SaveImage node is created we want to override the serialization of the output name widget to run our S&R
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

				const widget = this.widgets.find((w) => w.name === "filename_prefix");
				widget.serializeValue = () => {
					return applyTextReplacements(app, widget.value);
				};

				this.setProperty("Play sound", true);
				this.setProperty("Sound Volume", 0.9);

				this.playSound = () => {
					if (this.properties["Play sound"]) {
						let file = "assets/notify.mp3";
						file = new URL(file, import.meta.url);
						const url = new URL(file);
						const audio = new Audio(url);
						audio.volume = (this.properties["Sound Volume"] > 1) ? 1 : this.properties["Sound Volume"];
						audio.play();					
					}
				};
				
 				this.onPropertyChanged = (property, value) => {
					if (property == "Play sound"){
						if (value == true)
							this.title = this.title.replace('🔕', '🔔');
						else
							this.title = this.title.replace('🔔', '🔕');
					}
				};
				
				return r;
			};
		}
	},
});
