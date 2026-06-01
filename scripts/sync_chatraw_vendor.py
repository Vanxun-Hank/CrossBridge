#!/usr/bin/env python3
"""Download and verify the pinned ChatRaw frontend vendor assets.

The ChatRaw fork keeps its third-party JS/CSS out of git and fetches them here so a
fresh checkout (or ``apply_chatraw_patch.sh``) reproduces an identical, offline-capable
``backend/static/vendor/`` tree. Every artifact is pinned by URL **and** SHA-256; a
hash mismatch aborts the sync rather than silently shipping an unexpected build.

Usage:
    python3 scripts/sync_chatraw_vendor.py            # download + verify + install
    python3 scripts/sync_chatraw_vendor.py --check     # verify existing files only
"""
from __future__ import annotations

import argparse
import hashlib
import io
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = ROOT / "chatraw-fork" / "backend" / "static" / "vendor"
PDFJS_DIR = VENDOR_DIR / "pdfjs"

# Single-file libraries: (relative path under vendor/, url, sha256)
SINGLE_FILES = [
    (
        "alpine.min.js",
        "https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js",
        "c8fa8ff457abdcd212f37a07ef2f292c999011dffabcaa577fb1e1e0076ca658",
    ),
    (
        "alpine-collapse.min.js",
        "https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.13.3/dist/cdn.min.js",
        "2bd5d9719b537cdd83b80e171fd725da9cddaf9943d510fcb4ac0140db39a47a",
    ),
    (
        "marked.min.js",
        "https://cdn.jsdelivr.net/npm/marked@9.1.6/marked.min.js",
        "6002af63485b043fa60ddaba1b34363b98d2a8b2c63b607004f3a2405a8a053a",
    ),
]

# PDF.js: one pinned npm tarball, from which we extract only what the official-form
# viewer needs. CJK forms require cmaps; embedded-font fallback needs standard_fonts.
PDFJS_TARBALL_URL = "https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-5.7.284.tgz"
PDFJS_TARBALL_SHA = "f14db72530dec74fe666910e246242b9bb698df30f0e06622c4471b340a0413d"
PDFJS_VERSION = "5.7.284"
# tar member prefix -> destination subdir under vendor/pdfjs/
PDFJS_EXTRACT = {
    "package/build/pdf.mjs": "build/pdf.mjs",
    "package/build/pdf.worker.mjs": "build/pdf.worker.mjs",
    "package/web/pdf_viewer.mjs": "web/pdf_viewer.mjs",
    "package/web/pdf_viewer.css": "web/pdf_viewer.css",
    # Node-only build used by scripts/check_official_forms_pdfjs.mjs (no DOM globals).
    "package/legacy/build/pdf.mjs": "legacy/build/pdf.mjs",
    "package/legacy/build/pdf.worker.mjs": "legacy/build/pdf.worker.mjs",
}
# Directory members copied wholesale (member-prefix -> dest subdir)
PDFJS_EXTRACT_DIRS = {
    "package/cmaps/": "cmaps",
    "package/standard_fonts/": "standard_fonts",
    "package/web/images/": "web/images",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "CrossBridge vendor-sync/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def _verify(label: str, data: bytes, expected_sha: str) -> None:
    actual = _sha256_bytes(data)
    if actual != expected_sha:
        raise SystemExit(
            f"SHA-256 mismatch for {label}: expected {expected_sha}, got {actual}.\n"
            "Refusing to install an unexpected build — review the pinned source/version."
        )


def _check_only() -> int:
    problems: list[str] = []
    for rel, _url, sha in SINGLE_FILES:
        path = VENDOR_DIR / rel
        if not path.is_file() or _sha256_bytes(path.read_bytes()) != sha:
            problems.append(rel)
    for required in ("build/pdf.mjs", "build/pdf.worker.mjs", "web/pdf_viewer.mjs", "web/pdf_viewer.css"):
        if not (PDFJS_DIR / required).is_file():
            problems.append(f"pdfjs/{required}")
    if not (PDFJS_DIR / "cmaps").is_dir():
        problems.append("pdfjs/cmaps/")
    if problems:
        print("vendor assets MISSING or STALE:\n  - " + "\n  - ".join(problems))
        return 1
    print(f"vendor assets present and verified (pdfjs {PDFJS_VERSION}).")
    return 0


def _install_single_files() -> None:
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    for rel, url, sha in SINGLE_FILES:
        data = _download(url)
        _verify(rel, data, sha)
        (VENDOR_DIR / rel).write_bytes(data)
        print(f"  installed {rel} ({len(data)} bytes)")


def _install_pdfjs() -> None:
    data = _download(PDFJS_TARBALL_URL)
    _verify("pdfjs-dist tarball", data, PDFJS_TARBALL_SHA)
    if PDFJS_DIR.exists():
        shutil.rmtree(PDFJS_DIR)
    PDFJS_DIR.mkdir(parents=True, exist_ok=True)
    extracted = 0
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            name = member.name
            dest_rel: str | None = PDFJS_EXTRACT.get(name)
            if dest_rel is None:
                for prefix, dest_dir in PDFJS_EXTRACT_DIRS.items():
                    if name.startswith(prefix):
                        dest_rel = f"{dest_dir}/{name[len(prefix):]}"
                        break
            if dest_rel is None:
                continue
            dest = PDFJS_DIR / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            src = tar.extractfile(member)
            if src is None:
                continue
            dest.write_bytes(src.read())
            extracted += 1
    (PDFJS_DIR / "VERSION").write_text(PDFJS_VERSION + "\n", encoding="utf-8")
    print(f"  installed pdfjs {PDFJS_VERSION} ({extracted} files) under {PDFJS_DIR.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify existing files, do not download")
    args = parser.parse_args()
    if args.check:
        return _check_only()
    print(f"Syncing ChatRaw vendor assets into {VENDOR_DIR.relative_to(ROOT)} ...")
    _install_single_files()
    _install_pdfjs()
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
