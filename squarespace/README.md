# Squarespace overrides (Super CSS Inject)

Add these URLs in [Super CSS Inject](https://chromewebstore.google.com/detail/super-css-inject/pcfpmmmjdgngeidaggcahhoncahmpiin) → **Options** → stylesheet list. Use a short **alias** in the extension so the popup stays readable.

**Use jsDelivr URLs below** — `raw.githubusercontent.com/.../main/...` can lag behind `main` on the CDN (we saw `inject-probe.css` stale on raw while `main` was correct). jsDelivr `@main` tracked the repo tip immediately in testing.

Replace `main` in the path with a **commit SHA** (e.g. `@df60b9d`) if you need a frozen revision.

## Stylesheet URLs (copy-paste)

| Alias idea | URL (jsDelivr `@main`) |
| ---------- | ---------------------- |
| CTA test 1 | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/cta-test-1.css` |
| Header v1  | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/header-v1.css` |
| Inject probe | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/inject-probe.css` |

Equivalent raw GitHub (may be CDN-stale for some files):  
`https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/<file>.css`

After you **push** changes, allow a short delay for CDNs; hard-refresh the Squarespace tab if needed.

## Workflow

1. Edit a `.css` file in this folder.
2. Commit and push to `origin`.
3. Reload the page (or rely on your extension refresh behavior) to pick up the new file.

## More “sets”

Duplicate a file, rename it (e.g. `typography-tweaks.css`), push, and add its jsDelivr URL as another entry in the extension.

## Troubleshooting (injection vs selectors)

1. **Verify hosted CSS** (from repo root):  
   `python3 scripts/verify_remote_stylesheet.py`  
   Reads `.cursor/debug-d54107.log` for **H5** (jsDelivr probe) and **H6** (`raw` vs jsDelivr mismatch = stale raw).  
   Optionally: `VERIFY_STYLESHEET_URL='https://...' python3 scripts/verify_remote_stylesheet.py`

2. **Verify the extension injects anything** — add the **inject probe** jsDelivr URL in Super CSS Inject, activate it on your Squarespace tab, hard-refresh. You should see a **magenta inset frame** on the viewport. Remove the probe URL when done.

3. **If the probe works but CTAs do not change** — selectors in `cta-test-1.css` do not match your template. In DevTools, inspect a CTA, note its classes/tag, and add a matching selector (or share the outer HTML with your engineer).

### Magenta probe does not show (on Squarespace)

That usually means **the CSS never applies to the page** — not a CTA selector issue.

1. **Confirm the file loads** — Paste the probe URL into the address bar; you should see CSS text.
2. **Extension active on this tab** — Super CSS Inject popup: pick the probe (or CTA) stylesheet for **this** tab, then hard-refresh.
3. **CSP blocking external stylesheets** — Open DevTools → **Console** and look for messages like “Refused to load the stylesheet” / “Content Security Policy”. If present, URL-based injectors may not work on that site; use an extension that injects **inline** rules (e.g. [Stylus](https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne) or “User JavaScript and CSS”) and paste the contents of `cta-test-1.css` for your domain.
4. **Log CSP from your live URL** (helps narrow this down):

   `CHECK_PAGE_URL=https://your-published-site.com python3 scripts/verify_remote_stylesheet.py`

   Then read `.cursor/debug-d54107.log` for **H4** lines (`csp_headers` / `csp_fetch_failed`).

5. **Control test without Squarespace** — Open [`debug/local-probe.html`](../debug/local-probe.html) in Chrome. You should always see a **green top bar** (inline in the HTML). **Magenta inset** comes from CSS. If you see green but no magenta while using `file://`, Chrome may block linked styles; from the **repo root** run `python3 -m http.server 8765` and open `http://localhost:8765/debug/local-probe.html` instead.
