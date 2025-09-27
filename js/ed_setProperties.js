import {app} from "../../scripts/app.js";
import { applyTextReplacements } from "../../scripts/utils.js";

import { toggleWidget, findWidgetByName } from "./node_options/common/utils.js";

let is_playing_sound = false;

// Set Properties
app.registerExtension({
    name: "ED.SetProperties",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {

        // Efficient Loader 💬ED
		if (nodeData.name === "Efficient Loader 💬ED") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated?.apply(this, arguments);				
				
				this.setProperty("Use Latent Rebatch", true);
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
				this.setProperty("Use tiled VAE encode", false);

                return result;
            };
        }
		
		// KSampler (Efficient) 💬ED
		if (nodeData.name === "KSampler (Efficient) 💬ED") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;

			nodeType.prototype.onNodeCreated = function () {
				const result = onNodeCreated?.apply(this, arguments);

				// 초기 프로퍼티 설정
				this.setProperty("MaskDetailer mode", false);
				this.setProperty("(MaskDetailer) drop size", 5);
				this.setProperty("(MaskDetailer) cycle", 1);
				this.setProperty("(MaskDetailer) inpaint model enable", false);
				this.setProperty("(MaskDetailer) noise mask feather", 20);
				this.setProperty("Use tiled VAE decode", false);

				// 위젯 토글 함수 정의
				this.toggleWidgetByProperty = (value) => {
					const originalHeight = this.size[1];

					this.properties["MaskDetailer mode"] = value;

					// 필요한 위젯 목록
					const widgetNames = ["guide_size", "guide_size_for", "max_size", "feather", "crop_factor"];
					const widget_list = widgetNames
						.map(name => findWidgetByName(this, name))
						.filter(Boolean); // null 제거

					// 위젯 토글
					widget_list.forEach(widget => toggleWidget(this, widget, value));

					// 높이 조정
					if (this.size[1] < originalHeight) {
						this.setSize([this.size[0], originalHeight]);
					}

					this.setDirtyCanvas(true, true);
					// 플래시 처리
					//flashWidget(this, widget_list);
				};

				// 프로퍼티 변경시 토글 호출
				this.onPropertyChanged = (property, value) => {
					if (property === "MaskDetailer mode") {
						this.toggleWidgetByProperty(value);
					}
				};

				// 초기 상태 적용
				this.toggleWidgetByProperty(this.properties["MaskDetailer mode"]);

				return result;
			};
		}
		
		// Wildcard Encode 💬ED
        if (nodeData.name === "Wildcard Encode 💬ED") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated?.apply(this, arguments);
				this.setProperty("Turn on Apply Lora", false);
                return result;
            };
        }
		
		// FaceDetailer 💬ED, Detailer (SEGS) 💬ED
        if (nodeData.name === "FaceDetailer 💬ED" || nodeData.name === "Detailer (SEGS) 💬ED") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated?.apply(this, arguments);
				this.setProperty("Use tiled VAE decode", false);
                return result;
            };
        }
		
		// Save Image 🔔ED
		if (nodeData.name === "Save Image 🔔ED") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			// When the SaveImage node is created we want to override the serialization of the output name widget to run our S&R
			nodeType.prototype.onNodeCreated = function () {
				const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

				const widget = this.widgets.find((w) => w.name === "filename_prefix");
				widget.serializeValue = () => {
					return applyTextReplacements(app, widget.value);
				};

				this.setProperty("Play sound", true);
				this.setProperty("Sound Volume", 0.9);

				this.playSound = () => {
					if (this.properties["Play sound"] && !is_playing_sound) {
						is_playing_sound = true;
						let file = "assets/notify.mp3";
						file = new URL(file, import.meta.url);
						const url = new URL(file);
						const audio = new Audio(url);
						audio.volume = (this.properties["Sound Volume"] > 1) ? 1 : this.properties["Sound Volume"];
						audio.play();
						setTimeout(() => {is_playing_sound = false;}, 3000);
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
				return result;
			};
		}		
		
    },
});


