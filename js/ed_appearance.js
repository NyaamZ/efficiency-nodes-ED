import { app } from "../../scripts/app.js";

const COLOR_THEMES = {
    red: { nodeColor: "#322", nodeBgColor: "#533" },
    brown: { nodeColor: "#332922", nodeBgColor: "#593930" },
    green: { nodeColor: "#232", nodeBgColor: "#353" },
    blue: { nodeColor: "#223", nodeBgColor: "#335" },
    pale_blue: { nodeColor: "#2a363b", nodeBgColor: "#3f5159" },
    cyan: { nodeColor: "#233", nodeBgColor: "#355" },
    purple: { nodeColor: "#323", nodeBgColor: "#535" },
    yellow: { nodeColor: "#432", nodeBgColor: "#653" },
	yellow_ocher: { nodeColor: "#8c6446", nodeBgColor: "#785032" },
	dark_yellow: { nodeColor: "#332811", nodeBgColor: "#70561f" },
	sky_blue: { nodeColor: "#466d6e", nodeBgColor: "#325a5a" },
	sea_blue: { nodeColor: "#3c6446", nodeBgColor: "#285032" },
    black: { nodeColor: "#222", nodeBgColor: "#000", groupcolor: "#444" },
    none: { nodeColor: null, nodeBgColor: null } // no color
};

const NODE_THEME = {
	"Efficient Loader 💬ED": ["blue", "box"],
	"KSampler (Efficient) 💬ED": ["green", "box"],
	"KSampler Text 💬ED": ["green", "box"],
	"Load Image 💬ED": ["blue", "box"],
	"Save Image 🔔ED": ["red", "box"],

	"Refiner Script 💬ED": ["green", "box"],
	"Embedding Stacker 💬ED": ["blue", "box"],
	"LoRA Stacker 💬ED": ["blue", "box"],
	"Wildcard Encode 💬ED": ["blue", "box"],
	"Int Holder 💬ED": ["blue", "box"],
	
	"FaceDetailer 💬ED": ["yellow_ocher", "box"],
	"MaskDetailer 💬ED": ["yellow_ocher", "box"],
	"Detailer (SEGS) 💬ED": ["yellow_ocher", "box"],
	"Ultimate SD Upscale 💬ED": ["sea_blue", "box"],
	
	"SUPIR Model Loader 💬ED": ["sea_blue", "box"],
	"SUPIR Sampler 💬ED": ["sea_blue", "box"],

	"Regional Stacker 💬ED": ["yellow", "box"],
	"Regional Processor 💬ED": ["yellow", "box"],
	"Regional Script 💬ED": ["yellow", "box"],
	
	"Ext Model Input 💬ED": ["blue", "round"],

	"Context To BasicPipe": ["blue", "box"],
	"Context To DetailerPipe": ["blue", "box"],

	"Get Booru Tag 💬ED": ["cyan", "box"],
	"Simple Text 💬ED": ["cyan", "box"],
	"TIPO Script 💬ED": ["blue", "box"]
 };

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];  // Swap elements
    }
}

let colorKeys = Object.keys(COLOR_THEMES).filter(key => key !== "none");
shuffleArray(colorKeys);  // Shuffle the color themes initially

function setNodeColors(node, colorKey, shape) {
    if (!colorKey) return;
    node.shape = shape;	
	
	const theme = COLOR_THEMES[colorKey];
    if(theme.nodeColor && theme.nodeBgColor) {
        node.color = theme.nodeColor;
        node.bgcolor = theme.nodeBgColor;
    }
}

export function edAppearance_Init(node) {
	const nclass = node.comfyClass;
	if (NODE_THEME.hasOwnProperty(nclass)) {
		let colorKey = NODE_THEME[nclass][0];

		if (colorKey === "random") {
			// Check for a valid color key before popping
			if (colorKeys.length === 0 || !COLOR_THEMES[colorKeys[colorKeys.length - 1]]) {
				colorKeys = Object.keys(COLOR_THEMES).filter(key => key !== "none");
				shuffleArray(colorKeys);
			}
			colorKey = colorKeys.pop();
		}
		setNodeColors(node, colorKey, NODE_THEME[nclass][1]);
	}
}

/* 
app.registerExtension({
    name: "ED.Appearance",
    nodeCreated(node) {
        const nclass = node.comfyClass;
        if (NODE_THEME.hasOwnProperty(nclass)) {
            let colorKey = NODE_THEME[nclass][0];

            if (colorKey === "random") {
                // Check for a valid color key before popping
                if (colorKeys.length === 0 || !COLOR_THEMES[colorKeys[colorKeys.length - 1]]) {
                    colorKeys = Object.keys(COLOR_THEMES).filter(key => key !== "none");
                    shuffleArray(colorKeys);
                }
                colorKey = colorKeys.pop();
            }
            setNodeColors(node, colorKey, NODE_THEME[nclass][1]);
        }
    },
});
 */