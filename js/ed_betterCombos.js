import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";
import { $el } from "../../scripts/ui.js";
import { api } from "../../scripts/api.js";

const IMAGE_WIDTH = 384;
const IMAGE_HEIGHT = 384;

const NO_IMAGE_ICON = `url("data:image/svg+xml,%3C%3Fxml version='1.0'%3F%3E%3Csvg xmlns='http://www.w3.org/2000/svg' height='300px' width='300px' version='1.1' viewBox='-300 -300 600 600' font-family='Bitstream Vera Sans,Liberation Sans, Arial, sans-serif' font-size='72' text-anchor='middle'%3E%3Ccircle stroke='%23AAA' stroke-width='10' r='280' fill='%23FFF'/%3E%3Cswitch style='fill:%23444;'%3E%3Ctext id='trsvg3-bn' systemLanguage='bn'%3E%3Ctspan x='0' y='-8' id='trsvg1-bn'%3E&%23x99B;&%23x9AC;&%23x9BF; &%23x989;&%23x9AA;&%23x9B2;&%23x9AD;&%23x9CD;&%23x9AF;%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-bn'%3E&%23x9A8;&%23x9DF;%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-de' systemLanguage='de'%3E%3Ctspan x='0' y='-8' id='trsvg1-de'%3EKEIN BILD%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-de'%3EVERF&%23220;GBAR%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-en' systemLanguage='en'%3E%3Ctspan x='0' y='-8' id='trsvg1-en'%3ENO IMAGE%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-en'%3EAVAILABLE%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-es' systemLanguage='es'%3E%3Ctspan x='0' y='-8' id='trsvg1-es'%3EIMAGEN NO%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-es'%3EDISPONIBLE%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-id' systemLanguage='id'%3E%3Ctspan x='0' y='-8' id='trsvg1-id'%3EGAMBAR TAK%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-id'%3ETERSEDIA%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-ko' systemLanguage='ko'%3E%3Ctspan x='0' y='-8' id='trsvg1-ko'%3E&%23xC774;&%23xBBF8;&%23xC9C0;&%23xAC00;%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-ko'%3E&%23xC5C6;&%23xC2B5;&%23xB2C8;&%23xB2E4;%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-ro' systemLanguage='ro'%3E%3Ctspan x='0' y='-8' id='trsvg1-ro'%3EIMAGINE%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-ro'%3EINDISPONIBIL&%23x102;%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-tr' systemLanguage='tr'%3E%3Ctspan x='0' y='-8' id='trsvg1-tr'%3EG&%23xD6;R&%23xDC;NT&%23xDC;%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-tr'%3EYOK%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-vi' systemLanguage='vi'%3E%3Ctspan x='0' y='-8' id='trsvg1-vi'%3EKH&%23xD4;NG%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-vi'%3EC&%23xD3; &%23x1EA2;NH%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-ba' systemLanguage='ba'%3E%3Ctspan x='0' y='-8' id='trsvg1-ba'%3E&%23x4BA;&%23x4AE;&%23x420;&%23x4D8;&%23x422;&%23x422;&%23x4D8;&%23x420;%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-ba'%3E&%23x42E;&%23x4A0;%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-ang' systemLanguage='ang'%3E%3Ctspan x='0' y='-8' id='trsvg1-ang'%3EN&%23x100; BILDE%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-ang'%3E&%23x100;F&%23x112;R%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3-fr' systemLanguage='fr'%3E%3Ctspan x='0' y='-8' id='trsvg1-fr'%3EAUCUNE IMAGE%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2-fr'%3EDISPONIBLE%3C/tspan%3E%3C/text%3E%3Ctext id='trsvg3'%3E%3Ctspan x='0' y='-8' id='trsvg1'%3ENO IMAGE%3C/tspan%3E%3Ctspan x='0' y='80' id='trsvg2'%3EAVAILABLE%3C/tspan%3E%3C/text%3E%3C/switch%3E%3C/svg%3E%0A")`

const FOLDER_ICON = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' width='256' height='256' viewBox='0 0 256 256' xml:space='preserve'%3E%3Cdefs%3E%3C/defs%3E%3Cg style='stroke: none; stroke-width: 0; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: none; fill-rule: nonzero; opacity: 1;' transform='translate(1.4065934065934016 1.4065934065934016) scale(2.81 2.81)' %3E%3Cpath d='M 73.538 35.162 l -52.548 1.952 c -1.739 0 -2.753 0.651 -3.232 2.323 L 6.85 76.754 c -0.451 1.586 -2.613 2.328 -4.117 2.328 h 0 C 1.23 79.082 0 77.852 0 76.349 l 0 -10.458 V 23.046 v -2.047 v -6.273 c 0 -2.103 1.705 -3.808 3.808 -3.808 h 27.056 c 1.01 0 1.978 0.401 2.692 1.115 l 7.85 7.85 c 0.714 0.714 1.683 1.115 2.692 1.115 H 69.73 c 2.103 0 3.808 1.705 3.808 3.808 v 1.301 C 73.538 26.106 73.538 35.162 73.538 35.162 z' style='stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(224,173,49); fill-rule: nonzero; opacity: 1;' transform=' matrix(1 0 0 1 0 0) ' stroke-linecap='round' /%3E%3Cpath d='M 2.733 79.082 L 2.733 79.082 c 1.503 0 2.282 -1.147 2.733 -2.733 l 10.996 -38.362 c 0.479 -1.672 2.008 -2.824 3.748 -2.824 h 67.379 c 1.609 0 2.765 1.546 2.311 3.09 L 79.004 75.279 c -0.492 1.751 -1.571 3.818 -3.803 3.803 C 75.201 79.082 2.733 79.082 2.733 79.082 z' style='stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(255,200,67); fill-rule: nonzero; opacity: 1;' transform=' matrix(1 0 0 1 0 0) ' stroke-linecap='round' /%3E%3C/g%3E%3C/svg%3E")`

const GO_BACK_ICON = `url("data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3C!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools --%3E%3Csvg width='100px' height='100px' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' fill='none'%3E%3Cpath stroke='%23a3a3a3' opacity='0.9' stroke-linecap='square' stroke-linejoin='round' stroke-width='0.8' d='M11 18h3.75a5.25 5.25 0 100-10.5H5M7.5 4L4 7.5 7.5 11'/%3E%3C/svg%3E")`

const NONE_ICON = `url("data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3C!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools --%3E%3Csvg width='100px' height='100px' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' fill='none' opacity='0.9' stroke='%23a3a3a3' stroke-width='0.95' stroke-linecap='round' stroke-linejoin='miter'%3E%3Ccircle cx='12' cy='12' r='10'%3E%3C/circle%3E%3Ccircle cx='12' cy='12' r='10' fill='' opacity='0.1'%3E%3C/circle%3E%3Cline x1='5' y1='5' x2='19' y2='19'%3E%3C/line%3E%3C/svg%3E")`

const PLUG_ICON = `url("data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3C!DOCTYPE svg PUBLIC '-//W3C//DTD SVG 1.1//EN' 'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'%3E%3C!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools --%3E%3Csvg width='100px' height='100px' viewBox='-2.5 0 32 32' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Cg id='icomoon-ignore'%3E%3C/g%3E%3Cpath d='M18.804 18.457l-8.268 8.268-0.004-0.005c-0.031 0.032-0.056 0.067-0.088 0.097-2.147 2.147-5.642 2.147-7.789 0-2.085-2.085-2.139-5.435-0.176-7.593l1.103 1.102 1.743-1.742c2.339 1.116 5.221 0.712 7.159-1.225l2.968-2.967 0.742 0.742 0.742-0.742-2.968-2.967 4.451-4.451-0.742-0.742-4.451 4.451-2.967-2.967 4.45-4.451-0.741-0.742-4.451 4.451-2.967-2.967-0.742 0.742 0.742 0.742-2.968 2.967c-1.937 1.937-2.341 4.82-1.224 7.159l-1.743 1.742 1.122 1.123c-2.372 2.568-2.317 6.583 0.176 9.076 2.556 2.557 6.716 2.557 9.272 0l8.361-8.36c1.832-1.832 4.813-1.832 6.645 0l0.742-0.742c-2.241-2.241-5.889-2.241-8.129 0zM4.324 9.2l2.968-2.967 7.417 7.417-2.967 2.967c-2.045 2.045-5.372 2.045-7.418 0s-2.045-5.372-0-7.418zM2.907 16.551c0.202 0.283 0.422 0.555 0.675 0.808s0.527 0.474 0.808 0.675l-0.808 0.808-1.483-1.483 0.808-0.808z' fill='%23a3a3a3' fill-opacity='0.9'%3E%3C/path%3E%3C/svg%3E")`

const NODE_TYPES = {
  "Efficient Loader 💬ED": "checkpoints",
  "LoRA Stacker 💬ED": "loras",
  "Embedding Stacker 💬ED": "embeddings",
};

const WIDGET_NAMES = {
  checkpoints: "ckpt_name",
  loras: "lora_name",
  embeddings: "embedding_",
};

function getType(node) {
  return NODE_TYPES[node.comfyClass] || "error";
}

function getWidgetName(type) {
  return WIDGET_NAMES[type] || "error";
}

function encodeRFC3986URIComponent(str) {
	return encodeURIComponent(str).replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`);
}

const calculateImagePosition = (el, bodyRect) => {
	let { top, left, right } = el.getBoundingClientRect();
	const { width: bodyWidth, height: bodyHeight } = bodyRect;

	const isSpaceRight = right + IMAGE_WIDTH <= bodyWidth;
	if (isSpaceRight) {
		left = right;
	} else {
		left -= IMAGE_WIDTH;
	}

	top = top - IMAGE_HEIGHT / 2;
	if (top + IMAGE_HEIGHT > bodyHeight) {
		top = bodyHeight - IMAGE_HEIGHT;
	}
	if (top < 0) {
		top = 0;
	}

	return { left: Math.round(left), top: Math.round(top), isLeft: !isSpaceRight };
};

function showImage(relativeToEl, imageEl) {
	const bodyRect = document.body.getBoundingClientRect();
	if (!bodyRect) return;

	const { left, top, isLeft } = calculateImagePosition(relativeToEl, bodyRect);

	imageEl.style.left = `${left}px`;
	imageEl.style.top = `${top}px`;

	if (isLeft) {
		imageEl.classList.add("left");
	} else {
		imageEl.classList.remove("left");
	}

	document.body.appendChild(imageEl);
}

let imagesByType = {};
const loadImageList = async (type) => {
	imagesByType[type] = await (await api.fetchApi(`/pysssss/images/${type}`)).json();
};

app.registerExtension({
	name: "ED.betterCombos",
	init() {
		$el("style", {
			textContent: `
				.pysssss-combo-image {
					position: absolute;
					left: 0;
					top: 0;
					width: ${IMAGE_WIDTH}px;
					height: ${IMAGE_HEIGHT}px;
					object-fit: contain;
					object-position: top left;
					z-index: 9999;
				}
				.pysssss-combo-image.left {
					object-position: top right;
				}
				.pysssss-combo-folder { opacity: 0.7 }
				.pysssss-combo-folder-arrow { display: inline-block; width: 15px; }
				.pysssss-combo-folder:hover { background-color: rgba(255, 255, 255, 0.1); }
				.pysssss-combo-prefix { display: none }

				/* Special handling for when the filter input is populated to revert to normal */
				.litecontextmenu:has(input:not(:placeholder-shown)) .pysssss-combo-folder-contents {
					display: block !important;
				}
				.litecontextmenu:has(input:not(:placeholder-shown)) .pysssss-combo-folder { 
					display: none;
				}
				.litecontextmenu:has(input:not(:placeholder-shown)) .pysssss-combo-prefix { 
					display: inline;
				}
				.litecontextmenu:has(input:not(:placeholder-shown)) .litemenu-entry { 
					padding-left: 2px !important;
				}

				/* Grid mode */
				.pysssss-combo-grid {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
					gap: 10px;
					overflow-x: hidden;
					max-width: 60vw;
				}
				.pysssss-combo-grid .comfy-context-menu-filter {
					grid-column: 1 / -1;
					position: sticky;
					top: 0;
				}
				.pysssss-combo-grid .litemenu-entry {
					word-break: break-word;
					display: flex;
					flex-direction: column;
					justify-content: space-between;
					align-items: center;
				}
				.pysssss-combo-grid .litemenu-entry:before {
					content: "";
					display: block;
					width: 100%;
					height: 250px;
					background-size: contain;
					background-position: center;
					background-repeat: no-repeat;
					/* No-image image attribution: Picture icons created by Pixel perfect - Flaticon */
					background-image: var(--background-image, ${NO_IMAGE_ICON}) !important;
				}

			`,
			parent: document.body,
		});
		const p1 = loadImageList("checkpoints");
		const p2 = loadImageList("loras");
		const p3 = loadImageList("embeddings");

		const refreshComboInNodes = app.refreshComboInNodes;
		app.refreshComboInNodes = async function () {
			const r = await Promise.all([
				refreshComboInNodes.apply(this, arguments),
				loadImageList("checkpoints").catch(() => {}),
				loadImageList("loras").catch(() => {}),
				loadImageList("embeddings").catch(() => {}),
			]);
			return r[0];
		};

		const imageHost = $el("img.pysssss-combo-image");

		const positionMenu = (menu, fillWidth) => {
			// compute best position
			let left = app.canvas.last_mouse[0] - 10;
			let top = app.canvas.last_mouse[1] - 10;

			const body_rect = document.body.getBoundingClientRect();
			const root_rect = menu.getBoundingClientRect();

			if (body_rect.width && left > body_rect.width - root_rect.width - 10) left = body_rect.width - root_rect.width - 10;
			if (body_rect.height && top > body_rect.height - root_rect.height - 10) top = body_rect.height - root_rect.height - 10;

			menu.style.left = `${left}px`;
			menu.style.top = `${top}px`;
			if (fillWidth) {
				menu.style.right = "10px";
			}
		};

		const updateMenu = async (menu, type) => {
			try {
				await p1;
				await p2;
				await p3;
			} catch (error) {
				console.error(error);
				console.error("Error loading pysssss.betterCombos data")
			}

			// Clamp max height so it doesn't overflow the screen
			const position = menu.getBoundingClientRect();
			const maxHeight = window.innerHeight - position.top - 20;
			menu.style.maxHeight = `${maxHeight}px`;

			const images = imagesByType[type];
			const items = menu.querySelectorAll(".litemenu-entry");

			// Add image handler to items
			const addImageHandler = (item) => {
				const text = item.getAttribute("data-value").trim();
				if (images[text]) {
					const textNode = document.createTextNode("*");
					item.appendChild(textNode);

					item.addEventListener(
						"mouseover",
						() => {
							imageHost.src = `/pysssss/view/${encodeRFC3986URIComponent(images[text])}?${+new Date()}`;
							document.body.appendChild(imageHost);
							showImage(item, imageHost);
						},
						{ passive: true }
					);
					item.addEventListener(
						"mouseout",
						() => {
							imageHost.remove();
						},
						{ passive: true }
					);
					item.addEventListener(
						"click",
						() => {
							imageHost.remove();
						},
						{ passive: true }
					);
				}
			};

			const createTree = () => {
				// Create a map to store folder structures
				const folderMap = new Map();
				const rootItems = [];
				const splitBy = (navigator.platform || navigator.userAgent).includes("Win") ? /\/|\\/ : /\//;
				const itemsSymbol = Symbol("items");

				// First pass - organize items into folder structure
				for (const item of items) {
					const path = item.getAttribute("data-value").split(splitBy);

					// Remove path from visible text
					item.textContent = path[path.length - 1];
					if (path.length > 1) {
						// Add the prefix path back in so it can be filtered on
						const prefix = $el("span.pysssss-combo-prefix", {
							textContent: path.slice(0, -1).join("/") + "/",
						});
						item.prepend(prefix);
					}

					addImageHandler(item);

					if (path.length === 1) {
						rootItems.push(item);
						continue;
					}

					// Temporarily remove the item from current position
					item.remove();

					// Create folder hierarchy
					let currentLevel = folderMap;
					for (let i = 0; i < path.length - 1; i++) {
						const folder = path[i];
						if (!currentLevel.has(folder)) {
							currentLevel.set(folder, new Map());
						}
						currentLevel = currentLevel.get(folder);
					}

					// Store the actual item in the deepest folder
					if (!currentLevel.has(itemsSymbol)) {
						currentLevel.set(itemsSymbol, []);
					}
					currentLevel.get(itemsSymbol).push(item);
				}

				const createFolderElement = (name) => {
					const folder = $el("div.litemenu-entry.pysssss-combo-folder", {
						innerHTML: `<span class="pysssss-combo-folder-arrow">▶</span> ${name}`,
						style: { paddingLeft: "5px" },
					});
					return folder;
				};

				const insertFolderStructure = (parentElement, map, level = 0) => {
					for (const [folderName, content] of map.entries()) {
						if (folderName === itemsSymbol) continue;

						const folderElement = createFolderElement(folderName);
						folderElement.style.paddingLeft = `${level * 10 + 5}px`;
						parentElement.appendChild(folderElement);

						const childContainer = $el("div.pysssss-combo-folder-contents", {
							style: { display: "none" },
						});

						// Add items in this folder
						const items = content.get(itemsSymbol) || [];
						for (const item of items) {
							item.style.paddingLeft = `${(level + 1) * 10 + 14}px`;
							childContainer.appendChild(item);
						}

						// Recursively add subfolders
						insertFolderStructure(childContainer, content, level + 1);
						parentElement.appendChild(childContainer);

						// Add click handler for folder
						folderElement.addEventListener("click", (e) => {
							e.stopPropagation();
							const arrow = folderElement.querySelector(".pysssss-combo-folder-arrow");
							const contents = folderElement.nextElementSibling;
							if (contents.style.display === "none") {
								contents.style.display = "block";
								arrow.textContent = "▼";
							} else {
								contents.style.display = "none";
								arrow.textContent = "▶";
							}
						});
					}
				};

				insertFolderStructure(items[0].parentElement, folderMap);
				positionMenu(menu);
			};

			const addImageData = (item) => {
				const text = item.getAttribute("data-value").trim();
				if (images[text]) {
					item.style.setProperty("--background-image", `url(/pysssss/view/${encodeRFC3986URIComponent(images[text])})`);
				}
			};
			
			const checkCurrentLevelList = (currentLevel, item, folder_depth, path) => {
				if (!currentLevel["list"]) {
					currentLevel["list"] = [];
					makeGoBackIcon(currentLevel, item, folder_depth, path);					
				}				
			}

			const makeGoBackIcon = (currentLevel, item, folder_depth, path) => {				
				if (!folder_depth) return;

				const path_b = path.slice(0, folder_depth - 1)
				const value = path_b.join('\\');		
				const go_back_icon = $el("div.litemenu-entry.submenu", {
					innerHTML: `Back`,
					value: `${value}`,
				});
				go_back_icon.style.setProperty("--background-image", `${GO_BACK_ICON}`);
				go_back_icon.addEventListener("click", (e) => {
					e.stopPropagation();
					showHideIcon(go_back_icon.value);
				});
				menu.insertBefore(go_back_icon, item);
				folder_list.push(go_back_icon);
				currentLevel["list"].push(go_back_icon);
				return;
			}
			
			const makeFolderIcon = (currentLevel, item, folder_depth, path) => {

				const path_b = path.slice(0, folder_depth +1)
				const value = path_b.join('\\');
				const folder_icon = $el("div.litemenu-entry.submenu", {
					innerHTML: `${value}`,
					value: `${value}`,
				});
				folder_icon.style.setProperty("--background-image", `${FOLDER_ICON}`);				
				folder_icon.addEventListener("click", (e) => {
					e.stopPropagation();
					showHideIcon(folder_icon.value);
				});
				menu.insertBefore(folder_icon, item);
				folder_list.push(folder_icon);
				currentLevel["list"].push(folder_icon);
				return;
			}
			
			const iconChange = (item) => {
				item.style.removeProperty('color'); 
				item.style.removeProperty('background-color');

				if (item.value === "None") {
					item.style.setProperty("--background-image", `${NONE_ICON}`);
					item.style = "--background-image: " + NONE_ICON + ';';
					return true
				}
				else if(item.value === "🔌 model_opt input") {
					item.style.setProperty("--background-image", `${PLUG_ICON}`);
					//item.style = "--background-image: " + PLUG_ICON + ';';
					return true
				}
				return false
			}

			const buildFolderHierarchy = (items) => {
				const tree = {}; // JSON 구조를 위한 빈 객체
				const splitBy = (navigator.platform || navigator.userAgent).includes("Win") ? /\\|\// : /\//;

				for (const item of items) {
					const value = item.getAttribute("data-value").trim();
					const path = value.split(splitBy);
					let currentLevel = tree;

					for (let i = 0; i < path.length; i++) {
						const folder = path[i];

						if (i === path.length - 1) {
							// 파일이면 "list" 배열이 존재하는지 확인하고 push
							checkCurrentLevelList(currentLevel, item, i, path);
							currentLevel["list"].push(item);
							if (!iconChange(item)) addImageData(item);
							
						} else {
							// 폴더이면 객체 생성
							if (!currentLevel[folder]) {
								currentLevel[folder] = {};
								checkCurrentLevelList(currentLevel, item, i, path);
								makeFolderIcon(currentLevel, item, i, path);								
							}
							currentLevel = currentLevel[folder];
						}
					}
				}
				return tree;
			};

			const getFolderHierarchy = (folder_name, tree) => {
				if (folder_name.length === 0) {
					return tree["list"] || []; // 현재 경로에서 가능한 키(폴더/파일) 반환
				}
				const currentFolder = folder_name.shift(); // 첫 번째 요소 가져오기

				if (currentFolder in tree) {
					return getFolderHierarchy(folder_name, tree[currentFolder]); // 재귀적으로 탐색
				} else {
					return []; // 폴더가 존재하지 않으면 빈 배열 반환
				}
			};
			
			const showHideIcon = (folder_name) => {
				const splitBy = (navigator.platform || navigator.userAgent).includes("Win") ? /\\|\// : /\//;
				
				for (const el of [...items, ...folder_list]) {
					el.style.display = "none";
				}
				const folder_path = folder_name ? folder_name.split(splitBy) : [];
				const icons = getFolderHierarchy(folder_path, folderTree);
				if (icons){
					for (const icon of icons) {
						icon.style.display = "block";
					}
				}
			};
			
			let displaySetting = app.ui.settings.getSettingValue("pysssss.Combo++.Submenu");
			let folderTree = {};
			let folder_list = [];
			
			if (displaySetting === 1) {
				createTree();
			} else if (displaySetting === 2) {
				menu.classList.add("pysssss-combo-grid");
				
				folderTree = buildFolderHierarchy(items);
				showHideIcon("");
				// for (const item of items) {
					// addImageData(item);
				// }
				
				positionMenu(menu, true);
			} else {
				for (const item of items) {
					addImageHandler(item);
				}
			}
		};

		const mutationObserver = new MutationObserver((mutations) => {
			const node = app.canvas.node_over;

			if (!node || !NODE_TYPES[node.comfyClass]) {
				return;				
			}

			for (const mutation of mutations) {
				for (const removed of mutation.removedNodes) {
					if (removed.classList?.contains("litecontextmenu")) {
						imageHost.remove();
					}
				}

				for (const added of mutation.addedNodes) {
					if (added.classList?.contains("litecontextmenu")) {
						const overWidget = app.canvas.getWidgetAtCursor();
						const type = getType(node);
						if (overWidget?.name.includes(getWidgetName(type))) {
							requestAnimationFrame(() => {
								// Bad hack to prevent showing on right click menu by checking for the filter input
								if (!added.querySelector(".comfy-context-menu-filter")) return;
								updateMenu(added, type);
							});
						}
						return;
					}
				}
			}
		});
		mutationObserver.observe(document.body, { childList: true, subtree: false });
	},
});
