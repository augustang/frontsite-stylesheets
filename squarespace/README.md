# Squarespace overrides (Super CSS Inject)

Add these **raw** URLs in [Super CSS Inject](https://chromewebstore.google.com/detail/super-css-inject/pcfpmmmjdgngeidaggcahhoncahmpiin) → **Options** → stylesheet list. Use a short **alias** in the extension so the popup stays readable.

Replace `main` below if your default branch is different.

## Stylesheet URLs (copy-paste)

| Alias idea        | Raw URL |
| ----------------- | ------- |
| Sample (all areas) | `https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/sample-overrides.css` |
| Header v1         | `https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/header-v1.css` |

After you **push** changes, wait a moment or hard-refresh the Squarespace tab if the extension still shows old CSS (GitHub raw CDN cache).

## Workflow

1. Edit a `.css` file in this folder.
2. Commit and push to `origin`.
3. Reload the page (or rely on your extension refresh behavior) to pick up the new file.

## More “sets”

Duplicate a file, rename it (e.g. `typography-tweaks.css`), push, and add its raw URL as another entry in the extension.
