#!/usr/bin/env python3
"""Fetch and verify BOCHK official PDF forms into the ignored local cache."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "document_preparation" / "form_registry.json"
DEFAULT_CACHE_DIR = ROOT / "data" / "document_preparation" / "official_forms_cache"
ALLOWED_HOST = "www.bochk.com"


def _load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, destination: Path) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise ValueError(f"refusing non-BOCHK URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "CrossBridge official-form cache/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as target:
        shutil.copyfileobj(response, target)


def _verify_hash(path: Path, expected: str, label: str) -> None:
    actual = _sha256(path)
    if actual != expected:
        raise ValueError(
            f"{label} SHA-256 changed: expected {expected}, got {actual}. "
            "Review the new BOCHK source before updating the registry."
        )


def _inspect_pdf(path: Path) -> dict:
    try:
        output = subprocess.check_output(
            [
                "qpdf",
                "--json",
                "--json-key=acroform",
                "--json-key=encrypt",
                "--json-key=pages",
                str(path),
            ],
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("qpdf is required to verify official BOCHK PDFs") from exc
    return json.loads(output)


def _verify_pdf(path: Path, form: dict) -> None:
    _verify_hash(path, form["source_sha256"], form["form_id"])
    inspection = _inspect_pdf(path)
    acroform = inspection.get("acroform") or {}
    encryption = inspection.get("encrypt") or {}
    if not acroform.get("hasacroform"):
        raise ValueError(f"{form['form_id']} is no longer an AcroForm PDF")
    if len(inspection.get("pages") or []) != form["expected_pages"]:
        raise ValueError(f"{form['form_id']} page count changed")
    fields = acroform.get("fields") or []
    if len(fields) != form["expected_widget_count"]:
        raise ValueError(f"{form['form_id']} widget count changed")
    current_names = {field.get("fullname") for field in fields if field.get("fullname")}
    if not set(form["allowed_fields"]) <= current_names:
        raise ValueError(f"{form['form_id']} field names changed")
    method = (encryption.get("parameters") or {}).get("method")
    if method != form["encryption"]:
        raise ValueError(f"{form['form_id']} encryption changed: {method}")
    if not (encryption.get("capabilities") or {}).get("modifyforms"):
        raise ValueError(f"{form['form_id']} no longer permits form filling")


def _copy_verified(source: Path, destination: Path, form: dict) -> None:
    _verify_pdf(source, form)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    _verify_pdf(destination, form)


def fetch(cache_dir: Path) -> None:
    registry = _load_registry()
    forms = registry["forms"]
    direct_forms = [form for form in forms if not form["trade_terms_required"]]
    trade_forms = [form for form in forms if form["trade_terms_required"]]

    with tempfile.TemporaryDirectory(prefix="crossbridge-official-forms-") as temp:
        temp_dir = Path(temp)
        for form in direct_forms:
            downloaded = temp_dir / form["cache_filename"]
            _download(form["source_url"], downloaded)
            _copy_verified(downloaded, cache_dir / form["cache_filename"], form)

        terms_path = temp_dir / "trade_terms.html"
        archive_path = temp_dir / "trade_forms.zip"
        _download(registry["trade_terms"]["url"], terms_path)
        _verify_hash(terms_path, registry["trade_terms"]["sha256"], "trade terms")
        _download(registry["trade_archive"]["url"], archive_path)
        _verify_hash(archive_path, registry["trade_archive"]["sha256"], "trade archive")

        with ZipFile(archive_path) as archive:
            members = set(archive.namelist())
            for form in trade_forms:
                member = form["zip_member"]
                if member not in members:
                    raise ValueError(f"missing ZIP member for {form['form_id']}: {member}")
                extracted = temp_dir / form["cache_filename"]
                with archive.open(member) as source, extracted.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
                _copy_verified(extracted, cache_dir / form["cache_filename"], form)


def verify_cache(cache_dir: Path) -> None:
    registry = _load_registry()
    for form in registry["forms"]:
        path = cache_dir / form["cache_filename"]
        if not path.is_file():
            raise FileNotFoundError(f"missing cached form: {path}")
        _verify_pdf(path, form)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--accept-bochk-trade-terms", action="store_true")
    parser.add_argument("--verify-cache-only", action="store_true")
    args = parser.parse_args()

    if args.verify_cache_only:
        verify_cache(args.cache_dir)
    else:
        if not args.accept_bochk_trade_terms:
            raise SystemExit(
                "Refusing to download BOCHK trade e-forms without "
                "--accept-bochk-trade-terms. Read the terms URL in form_registry.json first."
            )
        fetch(args.cache_dir)
        verify_cache(args.cache_dir)
    print(f"Verified official BOCHK PDF cache: {args.cache_dir}")


if __name__ == "__main__":
    main()
