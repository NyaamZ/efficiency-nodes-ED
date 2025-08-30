import { api } from "../../../scripts/api.js";

import { rgthreeApi } from "./rgthree_api.js";
import { MenuButton, generateId, wait, injectCss, showMessage, hideMessage, showLoadingDialog } from "./shared_utils.js";
import { createElement as $el, empty, appendChildren, getClosestOrSelf, query, queryAll, setAttributes } from "./utils_dom.js";
import { logoCivitai, iconStar, link, pencilColored, diskColored, dotdotdot } from "./svgs.js";

//import { RgthreeDialog } from "../../rgthree/common/dialog.js";
export class RgthreeDialog extends EventTarget {
    constructor(options) {
        super();
        this.options = options;
        let container = $el("div.rgthree-dialog-container");
        this.element = $el("dialog", {
            classes: ["rgthree-dialog", options.class || ""],
            child: container,
            parent: document.body,
            events: {
                click: (event) => {
                    if (
                        !this.element.open ||
                        event.target === container ||
                        getClosestOrSelf(event.target, `.rgthree-dialog-container`) === container
                    ) {
                        return;
                    }
                    else if (
                        event.target.classList.contains("now-loading-dialog-container") ||
                        event.target.classList.contains("rgthree-top-messages-container")
                    ) {
                        // 자기 자신이면 return
                        return;
                    }
                    else if (
                        event.target.closest(".now-loading-dialog-container") ||
                        event.target.closest(".rgthree-top-messages-container")
                    ) {
                        // 자식 노드이면 a() 실행
                        return;
                    }

                    return this.close();
                },
            },

        });
        this.element.addEventListener("close", (event) => {
            this.onDialogElementClose();
        });
        this.titleElement = $el("div.rgthree-dialog-container-title", {
            parent: container,
            children: !options.title
                ? null
                : options.title instanceof Element || Array.isArray(options.title)
                    ? options.title
                    : typeof options.title === "string"
                        ? !options.title.includes("<h2")
                            ? $el("h2", { html: options.title })
                            : options.title
                        : options.title,
        });
        this.contentElement = $el("div.rgthree-dialog-container-content", {
            parent: container,
            child: options.content,
        });
        const footerEl = $el("footer.rgthree-dialog-container-footer", { parent: container });
        for (const button of options.buttons || []) {
            $el("button", {
                text: button.label,
                className: button.className,
                disabled: !!button.disabled,
                parent: footerEl,
                events: {
                    click: (e) => {
                        var _a;
                        (_a = button.callback) === null || _a === void 0 ? void 0 : _a.call(button, e);
                    },
                },
            });
        }
        if (options.closeButtonLabel !== false) {
            $el("button", {
                text: options.closeButtonLabel || "Close",
                className: "rgthree-button",
                parent: footerEl,
                events: {
                    click: (e) => {
                        this.close(e);
                    },
                },
            });
        }
    }
    setTitle(content) {
        const title = typeof content !== "string" || content.includes("<h2")
            ? content
            : $el("h2", { html: content });
        setAttributes(this.titleElement, { children: title });
    }
    setContent(content) {
        setAttributes(this.contentElement, { children: content });
    }
    show() {
        document.body.classList.add("rgthree-dialog-open");
        this.element.showModal();
        this.dispatchEvent(new CustomEvent("show"));
        return this;
    }
    async close(e) {
        if (this.options.onBeforeClose && !(await this.options.onBeforeClose())) {
            return;
        }
        this.element.close();
    }
    onDialogElementClose() {
        document.body.classList.remove("rgthree-dialog-open");
        this.element.remove();
        this.dispatchEvent(new CustomEvent("close", this.getCloseEventDetail()));
    }
    getCloseEventDetail() {
        return { detail: null };
    }
}

// import { CHECKPOINT_INFO_SERVICE, LORA_INFO_SERVICE } from "../../rgthree/common/model_info_service.js";
class BaseModelInfoService extends EventTarget {
    constructor() {
        super();
        this.fileToInfo = new Map();
        this.init();
    }
    init() {
        api.addEventListener(this.apiRefreshEventString, this.handleAsyncUpdate.bind(this));
    }
    async getInfo(file, refresh, light) {
        if (this.fileToInfo.has(file) && !refresh) {
            return this.fileToInfo.get(file);
        }
        return this.fetchInfo(file, refresh, light);
    }
    async refreshInfo(file) {
        return this.fetchInfo(file, true);
    }
    async clearFetchedInfo(file) {
        await rgthreeApi.clearModelsInfo({ type: this.modelType, files: [file] });
        this.fileToInfo.delete(file);
        return null;
    }
    async savePartialInfo(file, data) {
        let info = await rgthreeApi.saveModelInfo(this.modelType, file, data);
        this.fileToInfo.set(file, info);
        return info;
    }
    handleAsyncUpdate(event) {
        var _a;
        const info = (_a = event.detail) === null || _a === void 0 ? void 0 : _a.data;
        if (info === null || info === void 0 ? void 0 : info.file) {
            this.setFreshInfo(info.file, info);
        }
    }
    async fetchInfo(file, refresh = false, light = false) {
        var _a;
        let info = null;
        if (!refresh) {
            info = await rgthreeApi.getModelsInfo({ type: this.modelType, files: [file], light });
        }
        else {
            info = await rgthreeApi.refreshModelsInfo({ type: this.modelType, files: [file] });
        }
        info = (_a = info === null || info === void 0 ? void 0 : info[0]) !== null && _a !== void 0 ? _a : null;
        if (!light) {
            this.fileToInfo.set(file, info);
        }
        return info;
    }
    setFreshInfo(file, info) {
        this.fileToInfo.set(file, info);
    }
}
class LoraInfoService extends BaseModelInfoService {
    constructor() {
        super(...arguments);
        this.apiRefreshEventString = "rgthree-refreshed-loras-info";
        this.modelType = 'loras';
    }
}
class CheckpointInfoService extends BaseModelInfoService {
    constructor() {
        super(...arguments);
        this.apiRefreshEventString = "rgthree-refreshed-checkpoints-info";
        this.modelType = 'checkpoints';
    }
}
class EmbeddingInfoService extends BaseModelInfoService {
    constructor() {
        super(...arguments);
        this.apiRefreshEventString = "rgthree-refreshed-embeddings-info";
        this.modelType = 'embeddings';
    }
}
export const LORA_INFO_SERVICE = new LoraInfoService();
export const CHECKPOINT_INFO_SERVICE = new CheckpointInfoService();
export const EMBEDDING_INFO_SERVICE = new EmbeddingInfoService();

export function MODEL_INFO_SERVICE(modelType) {
    if (modelType === "loras") {
        return LORA_INFO_SERVICE;
    } else if (modelType === "checkpoints") {
        return CHECKPOINT_INFO_SERVICE;
    } else if (modelType === "embeddings") {
        return EMBEDDING_INFO_SERVICE;
    } else {
        return null;
    }
}


//###############################################################################

class RgthreeInfoDialog extends RgthreeDialog {
    isDevMode = false;

    constructor(file, modelType) {
        const dialogOptions = {
            class: "rgthree-info-dialog",
            title: `<h2>Loading...</h2>`,
            content: "<center>Loading..</center>",
            onBeforeClose: () => {
                hideMessage("fetch-civitai-waiting");
                return true;
            },
        };
        super(dialogOptions);
        this.modifiedModelData = false;
        this.modelInfo = null;
        this.modelType = modelType;
        this.init(file);
    }
    async init(file) {
        var _a, _b;
        const cssPromise = injectCss("rgthree/common/css/dialog_model_info.css");
        this.modelInfo = await this.getModelInfo(file);
        this.refreshPreviewImage();
        await cssPromise;
        this.setContent(this.getInfoContent());
        this.setTitle(((_a = this.modelInfo) === null || _a === void 0 ? void 0 : _a["name"]) || ((_b = this.modelInfo) === null || _b === void 0 ? void 0 : _b["file"]) || "Unknown");
        this.attachEvents();
    }
    refreshPreviewImage() {
        if (this.modelInfo?.images?.[0]?.url.includes("/rgthree/api/")) {
            this.modelInfo.images[0].url = ImgUrlWithTimestamp(this.modelInfo.images[0].url);
        }
    }
    getCloseEventDetail() {
        const detail = {
            dirty: this.modifiedModelData,
        };
        return { detail };
    }
    attachEvents() {
        this.contentElement.addEventListener("click", async (e) => {
            const target = getClosestOrSelf(e.target, "[data-action]");
            const action = target === null || target === void 0 ? void 0 : target.getAttribute("data-action");
            if (!target || !action) {
                return;
            }
            await this.handleEventAction(action, target, e);
        });
    }
    async handleEventAction(action, target, e) {
        var _a, _b;
        const info = this.modelInfo;
        if (!(info === null || info === void 0 ? void 0 : info.file)) {
            return;
        }
        if (action === "fetch-civitai") {
            if (this.modelType === "checkpoints") {
                showLoadingDialog({
                    id: "fetch-civitai-waiting",
                    type: "",
                    message: "Checkpoint loading is quiet long...",
                    timeout: 300000,
                });
            } else {
                showMessage({
                    id: "fetch-civitai-waiting",
                    type: "waiting",
                    message: ` Please wait for a moment...`,
                    timeout: 300000,
                });
            }
            await this.modleLoading(info);

            hideMessage("fetch-civitai-waiting");

            this.setContent(this.getInfoContent());
            this.setTitle(((_a = this.modelInfo) === null || _a === void 0 ? void 0 : _a["name"]) || ((_b = this.modelInfo) === null || _b === void 0 ? void 0 : _b["file"]) || "Unknown");
        }
        else if (action === "copy-trained-words") {
            const selected = queryAll(".-rgthree-is-selected", target.closest("tr"));
            const text = selected.map((el) => el.getAttribute("data-word")).join(", ");
            await navigator.clipboard.writeText(text);
            showMessage({
                id: "copy-trained-words-" + generateId(4),
                type: "success",
                message: `Successfully copied ${selected.length} key word${selected.length === 1 ? "" : "s"}.`,
                timeout: 4000,
            });
        }
        else if (action === "toggle-trained-word") {
            target === null || target === void 0 ? void 0 : target.classList.toggle("-rgthree-is-selected");
            const tr = target.closest("tr");
            if (tr) {
                const span = query("td:first-child > *", tr);
                let small = query("small", span);
                if (!small) {
                    small = $el("small", { parent: span });
                }
                const num = queryAll(".-rgthree-is-selected", tr).length;
                small.innerHTML = num
                    ? `${num} selected | <span role="button" data-action="copy-trained-words">Copy</span>`
                    : "";
            }
        }

        else if (action === "edit-row") {
            const tr = target.closest("tr");
            const td = query("td:nth-child(2)", tr);
            const input = td.querySelector("input,textarea");

            if (!input) {
                const fieldName = tr.dataset["fieldName"];
                tr.classList.add("-rgthree-editing");

                const isTextarea = fieldName === "userNote";
                let editor;

                // input 또는 textarea 생성
                if (isTextarea) {
                    editor = document.createElement("textarea");
                    editor.value = td.textContent.trim();
                } else {
                    editor = document.createElement("input");
                    editor.type = "text";
                    editor.value = td.textContent.trim();
                }

                // 키 이벤트 핸들러
                editor.addEventListener("keydown", (e) => {
                    if (!isTextarea && e.key === "Enter") {
                        const modified = saveEditableRow(info, tr, this.modelType, true);
                        this.modifiedModelData = this.modifiedModelData || modified;
                        e.stopPropagation();
                        e.preventDefault();
                    } else if (e.key === "Escape") {
                        const modified = saveEditableRow(info, tr, this.modelType, false);
                        this.modifiedModelData = this.modifiedModelData || modified;
                        e.stopPropagation();
                        e.preventDefault();
                    }
                });

                // td 비우고 editor 추가
                td.innerHTML = "";
                td.appendChild(editor);
                editor.focus();
            }
            else if (target.nodeName.toLowerCase() === "button") {
                const modified = saveEditableRow(info, tr, this.modelType, true);
                this.modifiedModelData = this.modifiedModelData || modified;
            }

            e?.preventDefault();
            e?.stopPropagation();
        }

        else if (action === "save-preview") {
            const figureEl = target.closest("figure");
            const imageUrl = figureEl?.querySelector("img")?.src;

            if (imageUrl) {
                await uploadPreview(imageUrl, this.modelType, this.modelInfo);
                this.modelInfo = await this.refreshModelInfo(this.modelInfo.file);
                this.refreshPreviewImage();
                this.setContent(this.getInfoContent());
            }
        }
    }

    async modleLoading(info) {
        const totalStart = performance.now();

        this.modelInfo = await this.refreshModelInfo(info.file);
        this.modelInfo.userNote = await getNote(this.modelInfo, this.modelType);
        MODEL_INFO_SERVICE(this.modelType).savePartialInfo(info.file, { ["userNote"]: this.modelInfo.userNote });
        await deleteFilesFromURL(this.modelType, this.modelInfo.file);

        const totalEnd = performance.now();
        console.log(`모델 로딩 시간: ${((totalEnd - totalStart) / 1000).toFixed(2)}초`);
    }

    getInfoContent() {
        var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o, _p, _q, _r, _s, _t, _u, _v, _w, _x, _y;
        const info = this.modelInfo || {};
        const civitaiLink = (_a = info.links) === null || _a === void 0 ? void 0 : _a.find((i) => i.includes("civitai.com/models"));
        const html = `
      <ul class="rgthree-info-area">
        <li title="Type" class="rgthree-info-tag -type -type-${(info.type || "").toLowerCase()}"><span>${info.type || ""}</span></li>
        <li title="Base Model" class="rgthree-info-tag -basemodel -basemodel-${(info.baseModel || "").toLowerCase()}"><span>${info.baseModel || ""}</span></li>
        <li class="rgthree-info-menu" stub="menu"></li>
        ${""}
      </ul>

      <table class="rgthree-info-table">
        ${infoTableRow("File", info.file || "")}
        ${infoTableRow("Hash (sha256)", info.sha256 || "")}
        ${civitaiLink
                ? infoTableRow("Civitai", `<a href="${civitaiLink}" target="_blank">${logoCivitai}View on Civitai</a>`)
                : ((_c = (_b = info.raw) === null || _b === void 0 ? void 0 : _b.civitai) === null || _c === void 0 ? void 0 : _c.error) === "Model not found"
                    ? infoTableRow("Civitai", '<i>Model not found</i> <span class="-help" title="The model was not found on civitai with the sha256 hash. It\'s possible the model was removed, re-uploaded, or was never on civitai to begin with."></span>')
                    : ((_e = (_d = info.raw) === null || _d === void 0 ? void 0 : _d.civitai) === null || _e === void 0 ? void 0 : _e.error)
                        ? infoTableRow("Civitai", (_g = (_f = info.raw) === null || _f === void 0 ? void 0 : _f.civitai) === null || _g === void 0 ? void 0 : _g.error)
                        : !((_h = info.raw) === null || _h === void 0 ? void 0 : _h.civitai)
                            ? infoTableRow("Civitai", `<button class="rgthree-button" data-action="fetch-civitai">Fetch info from civitai</button>`)
                            : ""}

        ${infoTableRow("Name", info.name || ((_k = (_j = info.raw) === null || _j === void 0 ? void 0 : _j.metadata) === null || _k === void 0 ? void 0 : _k.ss_output_name) || "", "The name for display.", "name")}

        ${!info.baseModelFile && !info.baseModelFile
                ? ""
                : infoTableRow("Base Model", (info.baseModel || "") + (info.baseModelFile ? ` (${info.baseModelFile})` : ""))}


        ${!((_l = info.trainedWords) === null || _l === void 0 ? void 0 : _l.length)
                ? ""
                : infoTableRow("Trained Words", (_m = getTrainedWordsMarkup(info.trainedWords)) !== null && _m !== void 0 ? _m : "", "Trained words from the metadata and/or civitai. Click to select for copy.")}

        ${!((_p = (_o = info.raw) === null || _o === void 0 ? void 0 : _o.metadata) === null || _p === void 0 ? void 0 : _p.ss_clip_skip) || ((_r = (_q = info.raw) === null || _q === void 0 ? void 0 : _q.metadata) === null || _r === void 0 ? void 0 : _r.ss_clip_skip) == "None"
                ? ""
                : infoTableRow("Clip Skip", (_t = (_s = info.raw) === null || _s === void 0 ? void 0 : _s.metadata) === null || _t === void 0 ? void 0 : _t.ss_clip_skip)}
        ${infoTableRow("Strength Min", (_u = info.strengthMin) !== null && _u !== void 0 ? _u : "", "The recommended minimum strength, In the Power Lora Loader node, strength will signal when it is below this threshold.", "strengthMin")}
        ${infoTableRow("Strength Max", (_v = info.strengthMax) !== null && _v !== void 0 ? _v : "", "The recommended maximum strength. In the Power Lora Loader node, strength will signal when it is above this threshold.", "strengthMax")}
        ${""}
        ${infoTableRow("Additional Notes", (_w = info.userNote) !== null && _w !== void 0 ? _w : "", "Additional notes you'd like to keep and reference in the info dialog.", "userNote")}

      </table>

      <ul class="rgthree-info-images">${(_y = (_x = info.images) === null || _x === void 0 ? void 0 : _x.map((img) => `
        <li>
          <figure>${img.type === 'video'
                        ? `<video src="${encodeFileNameInUrl(img.url)}" autoplay loop></video>`
                        : `<img src="${encodeFileNameInUrl(img.url)}" />`}
            <figcaption><!--
              -->${imgInfoField("", (img.civitaiUrl && img.type != 'video')
                            ? `<button class="ed-dialog-button-reset" data-action="save-preview">save as preview${iconStar}</button>`
                            : undefined, true, img.type === 'video')}<!--
              -->${imgInfoField("", img.civitaiUrl
                                ? `<a href="${img.civitaiUrl}" target="_blank">civitai${link}</a>`
                                : undefined)}<!--
			  <!--${""}--></figcaption>
          </figure>
        </li>`).join("")) !== null && _y !== void 0 ? _y : ""}</ul>
    `;

        const div = $el("div", { html });

        // 메뉴 옵션 기본
        const options = [
            { label: "More Actions", type: "title" },
            {
                label: "📁 Open with Windows Explorer",
                callback: async (e) => {
                    const url = `./ed_nodes/api/${this.modelType}/info/openfolder?files=${encodeURIComponent(this.modelInfo.file)}`;
                    fetch(url);
                },
            },
        ];

        // 개발 모드에서만 추가 옵션
        if (this.isDevMode) {
            options.push(
                {
                    label: "ℹ️ dialog TEST",
                    callback: async (e) => {
                        showLoadingDialog({
                            id: "fetch-civitai-waiting",
                            type: "",
                            message: "Checkpoint loading is quiet long...",
                            timeout: 3000,
                        });
                    },
                },
                {
                    label: "🧾 Open API JSON",
                    callback: async (e) => {
                        if (this.modelInfo?.file) {
                            window.open(`rgthree/api/loras/info?file=${encodeURIComponent(this.modelInfo.file)}`);
                        }
                    },
                },
                {
                    label: "🗑️ Clear all local info",
                    callback: async (e) => {
                        if (this.modelInfo?.file) {
                            this.modelInfo = await MODEL_INFO_SERVICE(this.modelType).clearFetchedInfo(this.modelInfo.file);
                            this.setContent(this.getInfoContent());
                            this.setTitle(this.modelInfo?.name || this.modelInfo?.file || "Unknown");
                        }
                    },
                }
            );
        }

        // 메뉴 버튼 생성
        setAttributes(query('[stub="menu"]', div), {
            children: [new MenuButton({ icon: dotdotdot, options })],
        });
        return div;
    }
}
export class RgthreeModelInfoDialog extends RgthreeInfoDialog {
    async getModelInfo(file) {
        return MODEL_INFO_SERVICE(this.modelType).getInfo(file, false, false);
    }
    async refreshModelInfo(file) {
        return MODEL_INFO_SERVICE(this.modelType).refreshInfo(file);
    }
    async clearModelInfo(file) {
        return MODEL_INFO_SERVICE(this.modelType).clearFetchedInfo(file);
    }
}

function infoTableRow(name, value, help = "", editableFieldName = "") {
    return `
    <tr class="${editableFieldName ? "editable" : ""}" ${editableFieldName ? `data-field-name="${editableFieldName}"` : ""}>
      <td><span>${name} ${help ? `<span class="-help" title="${help}"></span>` : ""}<span></td>
      <td ${editableFieldName ? "" : 'colspan="2"'}>${String(value).startsWith("<") ? value : `<span>${value}<span>`}</td>
      ${editableFieldName
            ? `<td style="width: 24px;"><button class="rgthree-button-reset rgthree-button-edit" data-action="edit-row">${pencilColored}${diskColored}</button></td>`
            : ""}
    </tr>`;
}
function getTrainedWordsMarkup(words) {
    let markup = `<ul class="rgthree-info-trained-words-list">`;
    for (const wordData of words || []) {
        markup += `<li title="${wordData.word}" data-word="${wordData.word}" class="rgthree-info-trained-words-list-item" data-action="toggle-trained-word">
      <span>${wordData.word}</span>
      ${wordData.civitai ? logoCivitai : ""}
      ${wordData.count != null ? `<small>${wordData.count}</small>` : ""}
    </li>`;
    }
    markup += `</ul>`;
    return markup;
}
function saveEditableRow(info, tr, modelType, saving = true) {
    var _a;
    const fieldName = tr.dataset["fieldName"];
    const input = query("input,textarea", tr);
    let newValue = (_a = info[fieldName]) !== null && _a !== void 0 ? _a : "";
    let modified = false;
    if (saving) {
        newValue = input.value;
        if (fieldName.startsWith("strength")) {
            if (Number.isNaN(Number(newValue))) {
                alert(`You must enter a number into the ${fieldName} field.`);
                return false;
            }
            newValue = (Math.round(Number(newValue) * 100) / 100).toFixed(2);
        }
        MODEL_INFO_SERVICE(modelType).savePartialInfo(info.file, { [fieldName]: newValue });
        modified = true;
    }
    tr.classList.remove("-rgthree-editing");
    const td = query("td:nth-child(2)", tr);
    appendChildren(empty(td), [$el("span", { text: newValue })]);
    return modified;
}
function imgInfoField(label, value, firstCaption = false, isVideo = false) {
    if (firstCaption && !isVideo) {
        return value != null ? `<span>${label ? `<label>${label} </label>` : ""}${value}</span>` : "Preview image";
    }
    else {
        return value != null ? `<span>${label ? `<label>${label} </label>` : ""}${value}</span>` : "";
    }
}

function encodeFileNameInUrl(url) {
    // 'file=' 이후부터 '&' 전까지 파일 이름 추출
    const fileMatch = url.match(/file=([^&]*)/);
    if (!fileMatch) return url; // file 파라미터 없으면 원본 반환

    const fileName = fileMatch[1];
    const encodedFileName = encodeURIComponent(fileName);

    // 원본 URL에서 파일 이름 부분만 교체
    return url.replace(fileName, encodedFileName);
}

async function uploadPreview(img_src, modelType, modelInfo) {
    try {
        // Fetch image as blob
        const response = await fetch(img_src);
        if (!response.ok) {
            throw new Error(`Failed to fetch image: ${response.status} ${response.statusText}`);
        }
        const blob = await response.blob();

        // Extract extension safely
        const url = new URL(img_src);
        const ext = url.pathname.split(".").pop() || "png";
        const name = `temp_preview.${ext}`;

        // Prepare upload body
        const body = new FormData();
        body.append("image", new File([blob], name, { type: blob.type }));
        body.append("overwrite", "true");
        body.append("type", "temp");

        // Upload image
        const resp = await api.fetchApi("/upload/image", {
            method: "POST",
            body,
        });

        if (!resp || resp.status !== 200) {
            console.error("Image upload failed:", resp);
            alert(`Error saving preview (${resp?.status || "?"}) ${resp?.statusText || ""}`);
            return;
        }

        // Save as preview
        await api.fetchApi(`/ed_nodes/save/${encodeURIComponent(`${modelType}/${modelInfo.file}`)}`, {
            method: "POST",
            body: JSON.stringify({
                filename: name,
                type: "temp",
            }),
            headers: {
                "content-type": "application/json",
            },
        });

        showMessage({
            id: "upload-preview-img-" + generateId(4),
            type: "success",
            message: `Successfully saved ${modelInfo.name} preview image.`,
            timeout: 4000,
        });
        // Refresh UI		
        app.refreshComboInNodes();

    } catch (err) {
        console.error("uploadPreview error:", err);
        alert(`Unexpected error: ${err.message}`);
    }
}

function ImgUrlWithTimestamp(img_url) {
    const separator = img_url.includes('?') ? '&' : '?';
    img_url = img_url + separator + `t=${Date.now()}`;
    return img_url;
}

async function getNote(modelInfo, modelType) {
    const note =
        (await getUserNote(modelType, modelInfo.file)) ||
        (modelInfo.sha256 ? await getCivitaiDescription(modelInfo.sha256) : "");

    return note;
}

async function deleteFilesFromURL(modelType, modelFile) {
    const deleteOK = app.ui.settings.getSettingValue("pysssss.ModelInfo.NsfwLevel");
    if (deleteOK && deleteOK != "PG13" && deleteOK != "PG") return;

    const url = `./ed_nodes/api/${modelType}/info/clear?files=${encodeURIComponent(modelFile)}`
    const res = await fetch(url);

    if (!res.ok) {
        if (res.status === 404) {
            console.log("dialog_info.js > deletefiles > Model not found");
            return "";
        }
        console.log(`dialog_info.js > deletefiles > Error loading info (${res.status}) ${res.statusText}`);
        return "";
    }
    const result = await res.json();
}

async function getCivitaiDescription(hash) {
    try {
        const res = await fetch(`https://civitai.com/api/v1/model-versions/by-hash/${hash}`);

        if (!res.ok) {
            if (res.status === 404) {
                console.log("dialog_info.js > getCivitaiDescription > Model not found");
                return "";
            }
            console.log(`dialog_info.js > getCivitaiDescription > Error loading info (${res.status}) ${res.statusText}`);
            return "";
        }

        const { description = "" } = await res.json();
        return description;
    } catch (err) {
        console.log("dialog_info.js > getCivitaiDescription > Failed to fetch civitai description:", err);
        return "";
    }
}

async function getUserNote(modelType, modelFile) {
    try {
        const url = `/ed_nodes/notedata/${encodeURIComponent(`${modelType}/${modelFile}`)}`
        const res = await api.fetchApi(url);

        if (!res.ok) {
            if (res.status === 404) {
                console.log("dialog_info.js > getUserNote > Note not found");
                return "";
            }
            console.log(`dialog_info.js > getUserNote > Error loading info (${res.status}) ${res.statusText}`);
            return "";
        }

        const data = await res.json();
        const note = data?.["pysssss.notes"] ?? "";
        return note;
    } catch (err) {
        console.log("dialog_info.js > getUserNote > Failed to fetch user note:", err);
        return "";
    }
}
