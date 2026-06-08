#!/usr/bin/env node
// Deploy-time compatibility check for the official BOCHK forms against the pinned PDF.js.
//
// For each registry form that is present in the local cache, it: opens the genuine PDF,
// writes one whitelisted field via annotationStorage, calls saveDocument(), re-opens the
// saved bytes, asserts the value persisted, and asserts the result is still encrypted
// (the original AES permissions must survive saveDocument — no flatten, no decryption).
//
// Requires the cache to be populated (scripts/fetch_official_forms.py) and the vendored
// PDF.js (scripts/sync_chatraw_vendor.py). Run: node scripts/check_official_forms_pdfjs.mjs
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const REGISTRY = path.join(ROOT, "data", "document_preparation", "form_registry.json");
const CACHE_DIR = path.join(ROOT, "data", "document_preparation", "official_forms_cache");
// The Node-only "legacy" build avoids browser globals (DOMMatrix, etc.).
const PDFJS = path.join(ROOT, "chatraw-fork", "backend", "static", "vendor", "pdfjs", "legacy", "build", "pdf.mjs");

// PDF.js is browser-oriented; provide just enough globals for module init. We never
// rasterise pages here (only getFieldObjects + annotationStorage + saveDocument), so
// these stubs are sufficient and @napi-rs/canvas is not required.
function polyfillDomGlobals() {
    const g = globalThis;
    if (typeof g.DOMMatrix === "undefined") {
        g.DOMMatrix = class DOMMatrix {
            constructor() {
                this.a = 1; this.b = 0; this.c = 0; this.d = 1; this.e = 0; this.f = 0;
            }
            static fromMatrix() { return new DOMMatrix(); }
            multiply() { return this; }
            translate() { return this; }
            scale() { return this; }
            inverse() { return this; }
        };
    }
    if (typeof g.Path2D === "undefined") g.Path2D = class Path2D {};
    if (typeof g.ImageData === "undefined") {
        g.ImageData = class ImageData {
            constructor(width, height) { this.width = width; this.height = height; }
        };
    }
}

async function main() {
    if (!existsSync(PDFJS)) {
        console.error(`PDF.js not vendored at ${PDFJS}. Run scripts/sync_chatraw_vendor.py first.`);
        process.exit(2);
    }
    polyfillDomGlobals();
    const pdfjsLib = await import(pathToFileUrl(PDFJS));
    const registry = JSON.parse(await readFile(REGISTRY, "utf-8"));

    let checked = 0;
    let skipped = 0;
    const failures = [];

    for (const form of registry.forms) {
        const pdfPath = path.join(CACHE_DIR, form.cache_filename);
        if (!existsSync(pdfPath)) {
            skipped += 1;
            console.log(`SKIP ${form.form_id}: not in local cache`);
            continue;
        }
        try {
            const bytes = new Uint8Array(await readFile(pdfPath));
            const doc = await pdfjsLib.getDocument({ data: bytes.slice(), useWorkerFetch: false, isEvalSupported: false }).promise;
            const fields = (await doc.getFieldObjects()) || {};
            const target = (form.allowed_fields || []).find((name) => fields[name] && fields[name][0]?.id);
            if (!target) throw new Error("no writable mapped field found");
            const annotationId = fields[target][0].id;
            const probe = "CROSSBRIDGE_PDFJS_CHECK";
            doc.annotationStorage.setValue(annotationId, { value: probe });
            const saved = await doc.saveDocument();

            const reopened = await pdfjsLib.getDocument({ data: saved.slice(), useWorkerFetch: false }).promise;
            const reFields = (await reopened.getFieldObjects()) || {};
            const reValue = reFields[target]?.[0]?.value;
            if (reValue !== probe) throw new Error(`value did not persist (got ${JSON.stringify(reValue)})`);

            // Original permission encryption must survive (AcroForm kept fillable, not flattened).
            const hadEncrypt = bytesInclude(bytes, "/Encrypt");
            const keepsEncrypt = bytesInclude(saved, "/Encrypt");
            if (hadEncrypt && !keepsEncrypt) throw new Error("encryption/permissions lost after saveDocument");

            checked += 1;
            console.log(
                `OK   ${form.form_id}: field "${target}" persisted; pages=${doc.numPages}; ` +
                `encrypted=${keepsEncrypt}`
            );
        } catch (error) {
            failures.push(`${form.form_id}: ${error.message || error}`);
            console.error(`FAIL ${form.form_id}: ${error.message || error}`);
        }
    }

    console.log(`\nchecked=${checked} skipped=${skipped} failed=${failures.length}`);
    if (failures.length) process.exit(1);
    if (checked === 0) {
        console.log("No cached forms to verify — populate the cache with scripts/fetch_official_forms.py.");
    }
    process.exit(0);
}

function pathToFileUrl(p) {
    return "file://" + p;
}

function bytesInclude(uint8, needle) {
    const hay = Buffer.from(uint8.buffer, uint8.byteOffset, uint8.byteLength).toString("latin1");
    return hay.includes(needle);
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
