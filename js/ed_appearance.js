import { app } from "../../scripts/app.js";

const COLOR_THEMES = {
    red: { nodeColor: "#332222", nodeBgColor: "#553333" },
    green: { nodeColor: "#223322", nodeBgColor: "#335533" },
    blue: { nodeColor: "#222233", nodeBgColor: "#333355" },
    pale_blue: { nodeColor: "#2a363b", nodeBgColor: "#3f5159" },
    cyan: { nodeColor: "#223333", nodeBgColor: "#335555" },
    purple: { nodeColor: "#332233", nodeBgColor: "#553355" },
    yellow: { nodeColor: "#443322", nodeBgColor: "#665533" },
	yellow_ocher: { nodeColor: "#8c6446", nodeBgColor: "#785032" },
	sky_blue: { nodeColor: "#466d6e", nodeBgColor: "#325a5a" },
	sea_blue: { nodeColor: "#3c6446", nodeBgColor: "#285032" },
    none: { nodeColor: null, nodeBgColor: null } // no color
};

const NODE_COLORS = {
	"Efficient Loader 💬ED": "random",
	// "Eff. Loader SDXL 💬ED": "random",
	"KSampler (Efficient) 💬ED": "random",
	// "KSampler SDXL (Eff.) 💬ED": "random",
	"KSampler Text 💬ED": "random",
	"Load Image 💬ED": "blue",
	"Save Image 🔔ED": "red",
	"Control Net Script 💬ED": "green",
	"Embedding Stacker 💬ED": "blue",
	"Apply LoRA Stack 💬ED": "blue",
	"Int Holder 💬ED": "blue",
	
	"FaceDetailer 💬ED": "sky_blue",
	"MaskDetailer 💬ED": "sky_blue",
	"Detailer (SEGS) 💬ED": "sky_blue",
	"Ultimate SD Upscale 💬ED": "sea_blue",
	
	"SUPIR model loader 💬ED": "sea_blue",
	"SUPIR Sampler 💬ED": "sea_blue",
 };

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];  // Swap elements
    }
}

let colorKeys = Object.keys(COLOR_THEMES).filter(key => key !== "none");
shuffleArray(colorKeys);  // Shuffle the color themes initially

function setNodeColors(node, theme) {
    if (!theme) {return;}
    node.shape = "box";
    if(theme.nodeColor && theme.nodeBgColor) {
        node.color = theme.nodeColor;
        node.bgcolor = theme.nodeBgColor;
    }
}

const ext = {
    name: "efficiency_ED.ed_appearance",

    nodeCreated(node) {
        const nclass = node.comfyClass;
        if (NODE_COLORS.hasOwnProperty(nclass)) {
            let colorKey = NODE_COLORS[nclass];

            if (colorKey === "random") {
                // Check for a valid color key before popping
                if (colorKeys.length === 0 || !COLOR_THEMES[colorKeys[colorKeys.length - 1]]) {
                    colorKeys = Object.keys(COLOR_THEMES).filter(key => key !== "none");
                    shuffleArray(colorKeys);
                }
                colorKey = colorKeys.pop();
            }

            const theme = COLOR_THEMES[colorKey];
            setNodeColors(node, theme);
        }
    }
};

app.registerExtension(ext);
