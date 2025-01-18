// Additional functions and imports
import { app } from "../../../scripts/app.js";

// A mapping for resolutions based on the type of the loader
const RESOLUTIONS = {
    "SD_15": [
        {width: 512, height: 512, ratio: "1:1", shape: "square"},
        {width: 1024, height: 1024, ratio: "1:1", shape: "square"}, 
        {width: 512, height: 640, ratio: "4:5", shape: "portrait"}, 
        {width: 512, height: 768, ratio: "2:3", shape: "portrait"},
        {width: 768, height: 512, ratio: "3:2", shape: "landscape"}, 
        {width: 640, height: 512, ratio: "5:4", shape: "landscape"},
        {width: 910, height: 512, ratio: "16:9", shape: "cinema"},
        {width: 952, height: 512, ratio: "1.85:1", shape: "cinema"},
        {width: 1024, height: 512, ratio: "2:1", shape: "cinema"},
        {width: 1224, height: 512, ratio: "2.39:1", shape: "anamorphic"}
    ],
    "SDXL": [
		{ratio: "1:1",width: 1024, height: 1024, shape: "◆square"},
        {ratio: "7:9",width: 896, height: 1152, shape: "◆portrait"},
        {ratio: "12:19",width: 768, height: 1216, shape: "portrait"},
		{ratio: "4:7",width: 768, height: 1344, shape: "◆portrait"},
		{ratio: "13:19",width: 832, height: 1216, shape: "◆portrait"},
		{ratio: "9:16",width: 720, height: 1280, shape: "portrait"},
        {ratio: "9:16",width: 756, height: 1344, shape: "portrait"},
        {ratio: "5:12",width: 640, height: 1536, shape: "◆portrait"},		
        {ratio: "9:7",width: 1152, height: 896, shape: "◆landscape"},
		{ratio: "19:13",width: 1216, height: 832, shape: "◆landscape"},
		{ratio: "16:9",width: 1024, height: 576, shape: "landscape"},
        {ratio: "7:4",width: 1344, height: 768, shape: "◆landscape"},
        {ratio: "12:5",width: 1536, height: 640, shape: "◆landscape"}		
    ]
};

// Function to set the resolution of a node
function setNodeResolution(node, width, height) {
	for (const w of node.widgets) {
		if (w.name.includes('width')){
			w.value = width;		
		}
		if (w.name.includes('height')){
			w.value = height;		
		}
	}
}

// The callback for the resolution submenu
function resolutionMenuCallback(node, width, height) {
    return function() {
        setNodeResolution(node, width, height);
    };
}

// Show the set resolution submenu
function showResolutionMenu(node, sdtype) {
    const resolutions = RESOLUTIONS[sdtype];
	let menu = [];
	
	for (const w of resolutions) {
		menu.push({
			content: `${w.ratio} - ${w.width} x ${w.height}  ${w.shape}`,
			callback: resolutionMenuCallback(node, w.width, w.height)
		});        
    }

/*     new LiteGraph.ContextMenu(resolutionOptions, {
        event: e,
        callback: null,
        parentMenu: menu,
        node: node
    }); */

    return menu;  // This ensures the original context menu doesn't proceed
}

/* // Extension Definition
app.registerExtension({
    name: "efficiency.SetResolution",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (["Efficient Loader", "Eff. Loader SDXL"].includes(nodeData.name)) {
            addMenuHandler(nodeType, function (insertOption) {
                insertOption({
                    content: "📐 Set Resolution...",
                    has_submenu: true,
                    callback: showResolutionMenu
                });
            });
        }
    },
}); */

app.registerExtension({
	name: "efficiency_ED.ed_setResolution",
	beforeRegisterNodeDef(nodeType) {

		if (nodeType.comfyClass.includes('Efficient Loader') || nodeType.comfyClass.includes('Eff. Loader') || nodeType.comfyClass.includes('Regional Stacker 💬ED') || nodeType.comfyClass.includes('Regional Processor 💬ED')) {
			let menu = [];			
			const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
			nodeType.prototype.getExtraMenuOptions = function (_, options) {
				
			menu.push({
				content: `SD 1.5`,
				submenu: { options: showResolutionMenu(this, "SD_15"), },
			});			
			menu.push({
				content: `SDXL`,
				submenu: { options: showResolutionMenu(this, "SDXL"), },
			});
			
			options.unshift({
				content: `📐 Aspect Ratio...`,
				submenu: { options: menu, },
			});
			menu = [];			
			return getExtraMenuOptions?.apply(this, arguments);
			};
		}
	},
});

