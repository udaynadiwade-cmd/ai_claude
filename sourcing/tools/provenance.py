"""Provenance records for every dataset written to data/.

A duty rate with no source and no date is a rumour. Each dataset directory
carries a MANIFEST.json naming where the bytes came from, when, and their
sha256, plus a staleness budget so the CLI can refuse to quote a rate that has
gone stale (CBIC exchange rates change fortnightly; tariff rates change with
every Finance Act and every effective-rate notification).
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone

MANIFEST = "MANIFEST.json"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_manifest(
    directory: str,
    dataset: str,
    source_name: str,
    source_url: str,
    files: list,
    max_age_days: int,
    licence: str = "",
    notes: str = "",
    extra: dict | None = None,
) -> dict:
    """Record what was fetched, from where, when, and how long it stays valid."""
    entries = []
    for name in files:
        path = os.path.join(directory, name)
        entries.append(
            {
                "file": name,
                "bytes": os.path.getsize(path),
                "sha256": sha256_file(path),
            }
        )
    manifest = {
        "dataset": dataset,
        "source_name": source_name,
        "source_url": source_url,
        "licence": licence,
        "fetched_at": now_iso(),
        "max_age_days": max_age_days,
        "files": entries,
        "notes": notes,
    }
    if extra:
        manifest.update(extra)
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, MANIFEST), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    return manifest


def read_manifest(directory: str) -> dict | None:
    path = os.path.join(directory, MANIFEST)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def age_days(manifest: dict) -> float:
    fetched = datetime.fromisoformat(manifest["fetched_at"])
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - fetched).total_seconds() / 86400


def is_stale(manifest: dict) -> bool:
    budget = manifest.get("max_age_days")
    if not budget:
        return False
    return age_days(manifest) > budget


def verify(directory: str) -> tuple[bool, list]:
    """Re-hash the files and confirm they match the manifest."""
    manifest = read_manifest(directory)
    if manifest is None:
        return False, ["no MANIFEST.json"]
    problems = []
    for entry in manifest.get("files", []):
        path = os.path.join(directory, entry["file"])
        if not os.path.exists(path):
            problems.append(f"missing: {entry['file']}")
            continue
        if sha256_file(path) != entry["sha256"]:
            problems.append(f"checksum mismatch: {entry['file']}")
    if is_stale(manifest):
        problems.append(
            f"stale: fetched {age_days(manifest):.1f} days ago, "
            f"budget {manifest['max_age_days']} days"
        )
    return not problems, problems


def describe(manifest: dict) -> str:
    stale = " STALE" if is_stale(manifest) else ""
    return (
        f"{manifest['dataset']}: {manifest['source_name']} "
        f"(fetched {manifest['fetched_at']}, age {age_days(manifest):.1f}d{stale})"
    )


def expiry(manifest: dict) -> str:
    budget = manifest.get("max_age_days")
    if not budget:
        return "no expiry set"
    fetched = datetime.fromisoformat(manifest["fetched_at"])
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    return (fetched + timedelta(days=budget)).date().isoformat()
