# Contributing Crown Profiles

Thanks for sharing a Crown layout.

## Bundle Requirements

- Use the `.crown.json` bundle exported by Moonlight V+.
- Do not edit the nested `profile.payload` by hand unless you also update its
  MD5 and SHA-256 checksums.
- Keep one profile per file.
- Use lowercase path names with hyphens, for example
  `profiles/apex-legends/fps-layout.crown.json`.

## Index Entry

Add a matching item to `index/v1.json`:

```json
{
  "bundleId": "crown.apex-legends.fps-layout.ab12cd34",
  "name": "Apex FPS Layout",
  "summary": "Fast access abilities and movement",
  "author": "your-github-name",
  "game": "Apex Legends",
  "tags": ["fps"],
  "updatedAt": "2026-06-18T00:00:00Z",
  "url": "../profiles/apex-legends/fps-layout.crown.json"
}
```

The app resolves `url` relative to `index/v1.json`, so profile paths should
usually start with `../profiles/`.

## Validate

```bash
python tools/validate_store.py
```

The validator checks the store index, duplicate entries, profile paths, bundle
schema version, bundle SHA-256, and the nested Crown payload MD5.
