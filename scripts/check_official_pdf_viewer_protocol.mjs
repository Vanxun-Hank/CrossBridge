#!/usr/bin/env node
// Regression check for the official-form iframe lifecycle.
//
// This executes the real viewer source with lightweight PDF.js and DOM mocks. It
// specifically covers the race where a delayed Form A draft event used to be saved
// as Form B after a quick form switch, plus stale/duplicate asynchronous PDF loads.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";

const viewerPath = new URL("../chatraw-fork/backend/static/official-pdf-viewer.js", import.meta.url);
const viewerUrl = "http://localhost/static/official-pdf-viewer.js";
const posted = [];
const windowHandlers = new Map();
const containerHandlers = new Map();
const documentLoads = [];

function delay(ms = 0) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function deferred() {
    let resolve;
    let reject;
    const promise = new Promise((resolvePromise, rejectPromise) => {
        resolve = resolvePromise;
        reject = rejectPromise;
    });
    return { promise, resolve, reject };
}

function createDocument(fieldName, annotationId) {
    const values = new Map();
    return {
        numPages: 1,
        destroyed: false,
        annotationStorage: {
            setValue(id, value) {
                values.set(id, { ...(values.get(id) || {}), ...value });
            },
            getValue(id, fallback) {
                return Object.assign(fallback, values.get(id) || {});
            },
        },
        async getFieldObjects() {
            return { [fieldName]: [{ id: annotationId }] };
        },
        async saveDocument() {
            return new Uint8Array([37, 80, 68, 70]);
        },
        async destroy() {
            this.destroyed = true;
        },
    };
}

class EventBus {
    constructor() {
        this.handlers = new Map();
    }

    on(name, callback) {
        this.handlers.set(name, callback);
    }
}

class PDFLinkService {
    setViewer(viewer) {
        this.viewer = viewer;
    }

    setDocument(document) {
        this.document = document;
    }
}

class PDFViewer {
    constructor() {
        this.currentScaleValue = "";
        this.document = null;
    }

    setDocument(document) {
        this.document = document;
    }
}

const statusElement = { textContent: "", style: {} };
const container = {
    clientWidth: 900,
    addEventListener(name, callback) {
        containerHandlers.set(name, callback);
    },
};

const pdfjsLib = {
    AnnotationMode: { ENABLE_FORMS: 1 },
    GlobalWorkerOptions: {},
    getDocument({ data }) {
        const pending = deferred();
        documentLoads.push({ marker: data[0], pending });
        return { promise: pending.promise };
    },
};

const context = vm.createContext({
    __pdfjsLib: pdfjsLib,
    Blob,
    EventBus,
    PDFLinkService,
    PDFViewer,
    ResizeObserver: class {
        observe() {}
    },
    URL,
    Uint8Array,
    clearTimeout,
    console,
    document: {
        body: { appendChild() {} },
        createElement() {
            return { click() {}, remove() {}, setAttribute() {}, style: {} };
        },
        getElementById(id) {
            return id === "status" ? statusElement : container;
        },
    },
    fetch: async (url) => ({
        ok: true,
        async arrayBuffer() {
            const marker = url.includes("form-a") ? 1 : url.includes("form-b") ? 2 : 3;
            return new Uint8Array([marker]).buffer;
        },
    }),
    requestAnimationFrame(callback) {
        callback();
    },
    setTimeout,
    window: {
        location: { origin: "http://localhost" },
        parent: {
            postMessage(message) {
                posted.push(message);
            },
        },
        addEventListener(name, callback) {
            if (!windowHandlers.has(name)) windowHandlers.set(name, []);
            windowHandlers.get(name).push(callback);
        },
    },
});

let source = await readFile(viewerPath, "utf8");
source = source
    .replace(/^import .*$/gm, "")
    .replaceAll("import.meta.url", JSON.stringify(viewerUrl));
vm.runInContext(`const pdfjsLib = globalThis.__pdfjsLib;\n${source}`, context, {
    filename: viewerPath.pathname,
});

function send(data) {
    for (const callback of windowHandlers.get("message") || []) {
        callback({ data: { source: "crossbridge-doc-prep", ...data }, origin: "http://localhost" });
    }
}

send({ type: "load-draft", packageId: "pkg-a", formId: "form-a", loadId: 1, pdfUrl: "/form-a.pdf", values: {} });
await delay();
assert.equal(documentLoads.length, 1, "first load should begin");

send({ type: "load-draft", packageId: "pkg-a", formId: "form-a", loadId: 1, pdfUrl: "/form-a.pdf", values: {} });
await delay();
assert.equal(documentLoads.length, 1, "duplicate lifecycle flush must not start a second PDF load");

send({ type: "load-draft", packageId: "pkg-b", formId: "form-b", loadId: 2, pdfUrl: "/form-b.pdf", values: {} });
await delay();
assert.equal(documentLoads.length, 2, "newer form selection should start its own load");

const formA = createDocument("Field A", "annotation-a");
const formB = createDocument("Field B", "annotation-b");
documentLoads[1].pending.resolve(formB);
await delay();
await delay();
documentLoads[0].pending.resolve(formA);
await delay();
await delay();

const loadedForms = posted.filter((message) => message.type === "ready" && message.formLoaded);
assert.deepEqual(
    loadedForms.map(({ packageId, formId, loadId }) => ({ packageId, formId, loadId })),
    [{ packageId: "pkg-b", formId: "form-b", loadId: 2 }],
    "a stale PDF completion must not replace the latest selected form",
);
assert.equal(formA.destroyed, true, "discarded stale PDF should be destroyed");

formB.annotationStorage.setValue("annotation-b", { value: "B saved value" });
containerHandlers.get("input")();
await delay(520);
assert.deepEqual(
    JSON.parse(JSON.stringify(posted.filter((message) => message.type === "draft-changed").at(-1))),
    {
        source: "official-pdf-viewer",
        type: "draft-changed",
        packageId: "pkg-b",
        formId: "form-b",
        loadId: 2,
        values: { "Field B": "B saved value" },
    },
    "draft changes must identify the package and form they came from",
);

formB.annotationStorage.setValue("annotation-b", { value: "flush before switch" });
containerHandlers.get("input")();
send({ type: "load-draft", packageId: "pkg-c", formId: "form-c", loadId: 3, pdfUrl: "/form-c.pdf", values: {} });
await delay();
assert.equal(
    posted.filter((message) => message.type === "draft-changed").at(-1).values["Field B"],
    "flush before switch",
    "switching forms must flush the previous form before replacing it",
);

const formC = createDocument("Field C", "annotation-c");
documentLoads[2].pending.resolve(formC);
await delay();
await delay();
formC.annotationStorage.setValue("annotation-c", { value: "discard me" });
containerHandlers.get("input")();
const draftCountBeforeUnload = posted.filter((message) => message.type === "draft-changed").length;
send({ type: "unload" });
await delay(520);
assert.equal(
    posted.filter((message) => message.type === "draft-changed").length,
    draftCountBeforeUnload,
    "discarding the viewer must cancel its pending draft timer",
);

console.log("official PDF viewer protocol race checks passed");
