import { app } from "../../../scripts/app.js";

const RESOLUTIONS = {
    "SD 1.5": [
        { width: 512, height: 512, ratio: "1:1", shape: "square" },
        { width: 1024, height: 1024, ratio: "1:1", shape: "square" },
        { width: 512, height: 640, ratio: "4:5", shape: "portrait" },
        { width: 512, height: 768, ratio: "2:3", shape: "portrait" },
        { width: 768, height: 512, ratio: "3:2", shape: "landscape" },
        { width: 640, height: 512, ratio: "5:4", shape: "landscape" },
        { width: 910, height: 512, ratio: "16:9", shape: "cinema" },
        { width: 952, height: 512, ratio: "1.85:1", shape: "cinema" },
        { width: 1024, height: 512, ratio: "2:1", shape: "cinema" },
        { width: 1224, height: 512, ratio: "2.39:1", shape: "anamorphic" },
    ],
    "SDXL": [
        { ratio: "1:1", width: 1024, height: 1024, shape: "◆square" },
        { ratio: "7:9", width: 896, height: 1152, shape: "◆portrait" },
        { ratio: "12:19", width: 768, height: 1216, shape: "portrait" },
        { ratio: "4:7", width: 768, height: 1344, shape: "◆portrait" },
        { ratio: "13:19", width: 832, height: 1216, shape: "◆portrait" },
        { ratio: "9:16", width: 720, height: 1280, shape: "portrait" },
        { ratio: "9:16", width: 756, height: 1344, shape: "portrait" },
        { ratio: "5:12", width: 640, height: 1536, shape: "◆portrait" },
        { ratio: "12:18", width: 1024, height: 1496, shape: "◆portrait" },
        { ratio: "9:7", width: 1152, height: 896, shape: "◆landscape" },
        { ratio: "19:13", width: 1216, height: 832, shape: "◆landscape" },
        { ratio: "16:9", width: 1024, height: 576, shape: "landscape" },
		{ ratio: "5:3", width: 1280, height: 768, shape: "◆landscape" },
        { ratio: "7:4", width: 1344, height: 768, shape: "◆landscape" },		
        { ratio: "18:12", width: 1496, height: 1024, shape: "◆landscape" },
        { ratio: "12:5", width: 1536, height: 640, shape: "◆landscape" },
    ],
};

const setNodeResolution = (node, width, height) => {
    node.widgets.forEach(w => {
        if (w.name.includes('width')) w.value = width;
        if (w.name.includes('height')) w.value = height;
    });
};

const createResolutionCallback = (node, width, height) => () => setNodeResolution(node, width, height);

const generateResolutionSubMenu = (node, resolutions) => resolutions.map(({ ratio, width, height, shape }) => ({
    content: `${ratio} - ${width} x ${height} ${shape}`,
    callback: createResolutionCallback(node, width, height)
}));

const generateResolutionMenu = node => Object.entries(RESOLUTIONS).map(([key, resolutions]) => ({
    content: key,
    submenu: { options: generateResolutionSubMenu(node, resolutions) }
}));

app.registerExtension({
    name: "ED.SetResolution",
    beforeRegisterNodeDef(nodeType) {
        if (["Efficient Loader 💬ED", "Regional Stacker 💬ED", "Regional Processor 💬ED"].some(cls => nodeType.comfyClass.includes(cls))) {
            const originalMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function (_, options) {
                options.unshift({
                    content: "📐 Aspect Ratio...",
                    submenu: { options: generateResolutionMenu(this) }
                });
                return originalMenuOptions?.apply(this, arguments);
            };
        }
    }
});
