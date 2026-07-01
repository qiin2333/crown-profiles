#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index" / "v1.json"
INDEX_URL = "https://raw.githubusercontent.com/qiin2333/crown-profiles/main/index/v1.json"


class ValidationError(Exception):
    pass


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


def md5_hex(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def sha256_hex(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_payload(payload_text, source):
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{source}: profile.payload is not valid JSON: {exc}") from exc

    for key in ("version", "settings", "elements", "md5"):
        if key not in payload:
            raise ValidationError(f"{source}: profile.payload missing {key}")

    version = payload["version"]
    settings = payload["settings"]
    elements = payload["elements"]
    expected_md5 = payload["md5"]
    actual_md5 = md5_hex(f"{version}{settings}{elements}")
    if actual_md5.lower() != str(expected_md5).lower():
        raise ValidationError(f"{source}: profile.payload md5 mismatch")

    try:
        json.loads(settings)
        json.loads(elements)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{source}: settings/elements JSON is invalid: {exc}") from exc


def validate_bundle(path):
    bundle = load_json(path)
    if bundle.get("kind") != "crown-profile-bundle":
        raise ValidationError(f"{path}: unsupported bundle kind")
    if bundle.get("schemaVersion") != 1:
        raise ValidationError(f"{path}: unsupported schemaVersion")

    profile = bundle.get("profile")
    if not isinstance(profile, dict):
        raise ValidationError(f"{path}: missing profile object")
    payload_text = profile.get("payload")
    expected_sha = profile.get("payloadSha256")
    if not payload_text or not expected_sha:
        raise ValidationError(f"{path}: missing profile payload or payloadSha256")
    actual_sha = sha256_hex(payload_text)
    if actual_sha.lower() != str(expected_sha).lower():
        raise ValidationError(f"{path}: profile payloadSha256 mismatch")
    validate_payload(payload_text, path)


def local_path_for_profile_url(profile_url):
    parsed = urlparse(profile_url)
    if parsed.scheme or parsed.netloc:
        raise ValidationError(f"Use repository-relative profile URLs, got {profile_url}")

    resolved = urljoin(INDEX_URL, profile_url)
    raw_prefix = "https://raw.githubusercontent.com/qiin2333/crown-profiles/main/"
    if not resolved.startswith(raw_prefix):
        raise ValidationError(f"Profile URL escapes repository root: {profile_url}")

    relative_path = resolved[len(raw_prefix):]
    path = (ROOT / relative_path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValidationError(f"Profile URL escapes repository root: {profile_url}")
    return path


def validate_index():
    index = load_json(INDEX_PATH)
    if index.get("kind") != "crown-profile-index":
        raise ValidationError("index/v1.json: unsupported kind")
    if index.get("schemaVersion") != 1:
        raise ValidationError("index/v1.json: unsupported schemaVersion")

    profiles = index.get("profiles")
    if not isinstance(profiles, list):
        raise ValidationError("index/v1.json: profiles must be an array")

    seen_urls = set()
    seen_bundle_ids = set()
    for i, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            raise ValidationError(f"index/v1.json: profiles[{i}] must be an object")
        name = str(profile.get("name", "")).strip()
        url = str(profile.get("url", "")).strip()
        if not name or not url:
            raise ValidationError(f"index/v1.json: profiles[{i}] missing name or url")
        if url in seen_urls:
            raise ValidationError(f"index/v1.json: duplicate url {url}")
        seen_urls.add(url)

        bundle_id = str(profile.get("bundleId", "")).strip()
        if bundle_id:
            if bundle_id in seen_bundle_ids:
                raise ValidationError(f"index/v1.json: duplicate bundleId {bundle_id}")
            seen_bundle_ids.add(bundle_id)

        bundle_path = local_path_for_profile_url(url)
        if not bundle_path.exists():
            raise ValidationError(f"index/v1.json: profile file does not exist: {url}")
        validate_bundle(bundle_path)


def validate_all_bundles():
    seen_bundle_ids = set()
    seen_payloads = set()
    for path in sorted((ROOT / "profiles").glob("**/*.crown.json")):
        validate_bundle(path)
        bundle = load_json(path)
        bundle_id = str(bundle.get("bundleId", "")).strip()
        if bundle_id:
            if bundle_id in seen_bundle_ids:
                raise ValidationError(f"duplicate bundleId {bundle_id}")
            seen_bundle_ids.add(bundle_id)

        profile = bundle.get("profile") or {}
        payload_sha = str(profile.get("payloadSha256", "")).strip()
        if payload_sha:
            if payload_sha in seen_payloads:
                raise ValidationError(f"duplicate profile payloadSha256 {payload_sha}")
            seen_payloads.add(payload_sha)


def main():
    try:
        validate_all_bundles()
        validate_index()
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("Crown store validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
