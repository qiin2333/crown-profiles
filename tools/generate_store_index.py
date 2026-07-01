#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = ROOT / "profiles"
INDEX_PATH = ROOT / "index" / "v1.json"


class IndexGenerationError(Exception):
    pass


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IndexGenerationError(f"{path}: invalid JSON: {exc}") from exc


def nested_name(value):
    if isinstance(value, dict):
        return str(value.get("name", "")).strip()
    return str(value or "").strip()


def profile_url(path):
    return "../" + path.relative_to(ROOT).as_posix()


def build_entry(path):
    bundle = load_json(path)
    if bundle.get("kind") != "crown-profile-bundle":
        raise IndexGenerationError(f"{path}: unsupported bundle kind")
    if bundle.get("schemaVersion") != 1:
        raise IndexGenerationError(f"{path}: unsupported schemaVersion")

    name = str(bundle.get("name") or bundle.get("profile", {}).get("name") or "").strip()
    if not name:
        raise IndexGenerationError(f"{path}: missing profile name")

    entry = {
        "bundleId": str(bundle.get("bundleId", "")).strip(),
        "name": name,
        "summary": str(bundle.get("summary", "")).strip(),
        "author": nested_name(bundle.get("author")),
        "game": nested_name(bundle.get("game")),
        "tags": [
            str(tag).strip()
            for tag in bundle.get("tags", [])
            if str(tag).strip()
        ],
        "updatedAt": str(bundle.get("updatedAt") or bundle.get("createdAt") or "").strip(),
        "url": profile_url(path),
    }

    layout_basis = bundle.get("layoutBasis")
    if isinstance(layout_basis, dict):
        entry["layoutBasis"] = layout_basis

    return entry


def build_index():
    profiles = []
    seen_bundle_ids = set()
    seen_urls = set()

    for path in sorted(PROFILE_ROOT.glob("**/*.crown.json")):
        entry = build_entry(path)
        url = entry["url"]
        if url in seen_urls:
            raise IndexGenerationError(f"duplicate profile url: {url}")
        seen_urls.add(url)

        bundle_id = entry.get("bundleId", "")
        if bundle_id:
            if bundle_id in seen_bundle_ids:
                raise IndexGenerationError(f"duplicate bundleId: {bundle_id}")
            seen_bundle_ids.add(bundle_id)

        profiles.append(entry)

    generated_at = max(
        (profile.get("updatedAt", "") for profile in profiles),
        default=""
    )
    return {
        "kind": "crown-profile-index",
        "schemaVersion": 1,
        "generatedAt": generated_at,
        "profiles": profiles,
    }


def main():
    try:
        index = build_index()
    except IndexGenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"Generated {INDEX_PATH.relative_to(ROOT)} with {len(index['profiles'])} profiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
