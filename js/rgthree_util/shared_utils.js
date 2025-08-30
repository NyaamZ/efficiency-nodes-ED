import { createElement as $el, getClosestOrSelf, setAttributes, queryAll } from "./utils_dom.js";

//from "../../rgthree/common/menu.js";
class Menu {
    constructor(options) {
        this.element = $el('menu.rgthree-menu');
        this.callbacks = new Map();
        this.handleWindowPointerDownBound = this.handleWindowPointerDown.bind(this);
        this.setOptions(options);
        this.element.addEventListener('pointerup', async (e) => {
            var _a, _b;
            const target = getClosestOrSelf(e.target, "[data-callback],menu");
            if (e.which !== 1) {
                return;
            }
            const callback = (_a = target === null || target === void 0 ? void 0 : target.dataset) === null || _a === void 0 ? void 0 : _a['callback'];
            if (callback) {
                const halt = await ((_b = this.callbacks.get(callback)) === null || _b === void 0 ? void 0 : _b(e));
                if (halt !== false) {
                    this.close();
                }
            }
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
        });
    }
    setOptions(options) {
        for (const option of options) {
            if (option.type === 'title') {
                this.element.appendChild($el(`li`, {
                    html: option.label
                }));
            }
            else {
                const id = generateId(8);
                this.callbacks.set(id, async (e) => { var _a; return (_a = option === null || option === void 0 ? void 0 : option.callback) === null || _a === void 0 ? void 0 : _a.call(option, e); });
                this.element.appendChild($el(`li[role="button"][data-callback="${id}"]`, {
                    html: option.label
                }));
            }
        }
    }
    toElement() {
        return this.element;
    }
    async open(e) {
        const parent = e.target.closest('div,dialog,body');
        parent.appendChild(this.element);
        setAttributes(this.element, {
            style: {
                left: `${e.clientX + 16}px`,
                top: `${e.clientY - 16}px`,
            }
        });
        this.element.setAttribute('state', 'measuring-open');
        await wait(16);
        const rect = this.element.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            this.element.style.left = `${e.clientX - rect.width - 16}px`;
            await wait(16);
        }
        this.element.setAttribute('state', 'open');
        setTimeout(() => {
            window.addEventListener('pointerdown', this.handleWindowPointerDownBound);
        });
    }
    handleWindowPointerDown(e) {
        if (!this.element.contains(e.target)) {
            this.close();
        }
    }
    async close() {
        window.removeEventListener('pointerdown', this.handleWindowPointerDownBound);
        this.element.setAttribute('state', 'measuring-closed');
        await wait(16);
        this.element.setAttribute('state', 'closed');
        this.element.remove();
    }
    isOpen() {
        return (this.element.getAttribute('state') || '').includes('open');
    }
}
export class MenuButton {
    constructor(options) {
        this.element = $el('button.rgthree-button[data-action="open-menu"]');
        this.options = options;
        this.element.innerHTML = options.icon;
        this.menu = new Menu(options.options);
        this.element.addEventListener('pointerdown', (e) => {
            if (!this.menu.isOpen()) {
                this.menu.open(e);
            }
        });
    }
    toElement() {
        return this.element;
    }
}

export function wait(ms = 16) {
    if (ms === 16) {
        return new Promise((resolve) => {
            requestAnimationFrame(() => {
                resolve();
            });
        });
    }
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve();
        }, ms);
    });
}

function dec2hex(dec) {
    return dec.toString(16).padStart(2, "0");
}
export function generateId(length) {
    const arr = new Uint8Array(length / 2);
    crypto.getRandomValues(arr);
    return Array.from(arr, dec2hex).join("");
}

export function injectCss(href) {
    if (document.querySelector(`link[href^="${href}"]`)) {
        return Promise.resolve();
    }
    return new Promise((resolve) => {
        const link = document.createElement("link");
        link.setAttribute("rel", "stylesheet");
        link.setAttribute("type", "text/css");
        const timeout = setTimeout(resolve, 1000);
        link.addEventListener("load", (e) => {
            clearInterval(timeout);
            resolve();
        });
        link.href = href;
        document.head.appendChild(link);
    });
}

export async function showMessage(data) {
    let container = document.querySelector(".rgthree-top-messages-container");
    if (!container) {
        container = document.createElement("div");
        container.classList.add("rgthree-top-messages-container");
        document.body.appendChild(container);
    }
    container.style.display = "flex";
    const dialogs = queryAll("dialog[open]");
    if (dialogs.length) {
        let dialog = dialogs[dialogs.length - 1];
        dialog.appendChild(container);
        dialog.addEventListener("close", (e) => {
            document.body.appendChild(container);
        });
    }
    await hideMessage(data.id);
    const messageContainer = document.createElement("div");
    messageContainer.setAttribute("type", data.type || "info");
    const message = document.createElement("span");
    message.innerHTML = data.message;
    messageContainer.appendChild(message);
    for (let a = 0; a < (data.actions || []).length; a++) {
        const action = data.actions[a];
        if (a > 0) {
            const sep = document.createElement("span");
            sep.innerHTML = "&nbsp;|&nbsp;";
            messageContainer.appendChild(sep);
        }
        const actionEl = document.createElement("a");
        actionEl.innerText = action.label;
        if (action.href) {
            actionEl.target = "_blank";
            actionEl.href = action.href;
        }
        if (action.callback) {
            actionEl.onclick = (e) => {
                return action.callback(e);
            };
        }
        messageContainer.appendChild(actionEl);
    }
    const messageAnimContainer = document.createElement("div");
    messageAnimContainer.setAttribute("msg-id", data.id);
    messageAnimContainer.appendChild(messageContainer);
    container.appendChild(messageAnimContainer);
    await wait(64);
    messageAnimContainer.style.marginTop = `-${messageAnimContainer.offsetHeight}px`;
    await wait(64);
    messageAnimContainer.classList.add("-show");
    if (data.timeout) {
        await wait(data.timeout);
        hideMessage(data.id);
    }
}

export async function hideMessage(id) {
    // 두 컨테이너에서 msg 요소 검색
    const msg = document.querySelector(
        `.now-loading-dialog-container > [msg-id="${id}"], .rgthree-top-messages-container > [msg-id="${id}"]`
    );
    if (!msg) return; // msg가 없으면 바로 종료

    if (msg.classList.contains("-show")) {
        msg.classList.remove("-show");
        await wait(750);
    }

    const parent = msg.parentElement;
    msg.remove();
    if (parent && parent.children.length === 0) {
        parent.style.display = "none";
    }
}

export async function showLoadingDialog(data) {

    function setRandomLoadingGif(element) {
        const gifs = [
            "/extensions/efficiency-nodes-ED/assets/nowloading.gif",
            "/extensions/efficiency-nodes-ED/assets/tap-waiting.gif"
        ];
        const index = Math.floor(Math.random() * gifs.length);
        const selectedGif = gifs[index];

        const img = new Image();
        img.onload = () => {
            // 이미지 로드 완료 후에 background 적용
            element.style.backgroundImage = `url("${selectedGif}")`;
        };
        img.src = selectedGif;
    }

    let container = document.querySelector(".now-loading-dialog-container");
    if (!container) {
        container = document.createElement("div");
        container.classList.add("now-loading-dialog-container");
        document.body.appendChild(container);
    }
    container.style.display = "flex";
    const dialogs = queryAll("dialog[open]");
    if (dialogs.length) {
        let dialog = dialogs[dialogs.length - 1];
        dialog.appendChild(container);
        dialog.addEventListener("close", (e) => {
            document.body.appendChild(container);
        });
    }
    await hideMessage(data.id);
    const messageContainer = document.createElement("div");
    messageContainer.setAttribute("type", data.type || "info");

    setRandomLoadingGif(messageContainer);

    const message = document.createElement("span");
    message.innerHTML = data.message;
    messageContainer.appendChild(message);
    for (let a = 0; a < (data.actions || []).length; a++) {
        const action = data.actions[a];
        if (a > 0) {
            const sep = document.createElement("span");
            sep.innerHTML = "&nbsp;|&nbsp;";
            messageContainer.appendChild(sep);
        }
        const actionEl = document.createElement("a");
        actionEl.innerText = action.label;
        if (action.href) {
            actionEl.target = "_blank";
            actionEl.href = action.href;
        }
        if (action.callback) {
            actionEl.onclick = (e) => {
                return action.callback(e);
            };
        }
        messageContainer.appendChild(actionEl);
    }
    const messageAnimContainer = document.createElement("div");
    messageAnimContainer.setAttribute("msg-id", data.id);
    messageAnimContainer.appendChild(messageContainer);
    container.appendChild(messageAnimContainer);
    await wait(64);
    messageAnimContainer.style.marginTop = `-${messageAnimContainer.offsetHeight}px`;
    await wait(64);

    // transition 적용 전에 강제로 reflow (안정적으로 보여주기)
    void messageAnimContainer.offsetWidth;

    messageAnimContainer.classList.add("-show");
    if (data.timeout) {
        await wait(data.timeout);
        hideMessage(data.id);
    }
}
