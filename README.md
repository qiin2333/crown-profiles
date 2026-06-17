# Crown Profiles

Community Crown profile store for Moonlight V+.

Moonlight V+ reads this repository as a static store. The app downloads
`index/v1.json`, shows the published profiles, then downloads the selected
`.crown.json` bundle from this repository.

## Store URL

```text
https://raw.githubusercontent.com/qiin2333/crown-profiles/main/index/v1.json
```

## Repository Layout

```text
index/v1.json                  Store index consumed by the app
profiles/<game>/<profile>.json Published Crown profile bundles
schemas/                       JSON schema references
tools/validate_store.py        Local/CI validation
```

## Submit a Profile

### From Moonlight V+

1. Open Crown Configuration Management.
2. Choose "Publish to Crown Store".
3. Authorize GitHub when prompted.
4. Pick a local Crown profile and fill in the Store listing.
5. Moonlight V+ will fork this repository, commit the profile bundle and index
   update, then open a pull request from your GitHub account.

The app asks GitHub for public repository access only so it can create that
fork, branch, commit, and pull request. It does not receive direct write access
to the main store branch.

### Manually

1. Export a Crown share package from Moonlight V+.
2. Add the `.crown.json` file under `profiles/<game>/`.
3. Add one entry to `index/v1.json`.
4. Run `python tools/validate_store.py`.
5. Open a pull request.

If you are submitting from a phone, open an issue with the "Submit Crown
Profile" template and attach the exported `.crown.json` file. A maintainer can
move it into the index after validation.

Moonlight V+ should never embed a repository write token. Fully direct in-app
publishing must use the user's GitHub authorization and open a pull request
from the user's account.
