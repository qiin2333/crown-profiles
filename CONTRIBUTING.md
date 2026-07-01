# Contributing Crown Profiles

Thanks for sharing a Crown layout.

## Bundle Requirements

- Use the `.crown.json` bundle exported by Moonlight V+.
- Do not edit the nested `profile.payload` by hand unless you also update its
  MD5 and SHA-256 checksums.
- Keep one profile per file.
- Use lowercase path names with hyphens, for example
  `profiles/apex-legends/fps-layout.crown.json`.

## Store Index

Do not edit `index/v1.json` in profile submissions. It is generated from the
files under `profiles/` after a pull request is merged.

## Validate

```bash
python tools/validate_store.py
```

The validator checks the store index, duplicate entries, profile paths, every
profile bundle schema version, bundle SHA-256, and the nested Crown payload MD5.
