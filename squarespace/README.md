# Squarespace overrides (Super CSS Inject)

Add these **raw** URLs in [Super CSS Inject](https://chromewebstore.google.com/detail/super-css-inject/pcfpmmmjdgngeidaggcahhoncahmpiin) → **Options** → stylesheet list. Use a short **alias** in the extension so the popup stays readable.

Replace `main` below if your default branch is different.

## Stylesheet URLs (copy-paste)

| Alias idea   | Raw URL |
| ------------ | ------- |
| CTA test 1   | `https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/cta-test-1.css` |
| Header v1    | `https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/header-v1.css` |

After you **push** changes, wait a moment or hard-refresh the Squarespace tab if the extension still shows old CSS (GitHub raw CDN cache).

## Workflow

1. Edit a `.css` file in this folder.
2. Commit and push to `origin`.
3. Reload the page (or rely on your extension refresh behavior) to pick up the new file.

## More “sets”

Duplicate a file, rename it (e.g. `typography-tweaks.css`), push, and add its raw URL as another entry in the extension.

## Troubleshooting (injection vs selectors)

1. **Verify GitHub serves your CSS** (from repo root):  
   `python3 scripts/verify_remote_stylesheet.py`  
   Optionally: `VERIFY_STYLESHEET_URL='https://raw.githubusercontent.com/.../other.css' python3 scripts/verify_remote_stylesheet.py`

2. **Verify the extension injects anything** — push `inject-probe.css`, add its raw URL in Super CSS Inject, activate it on your Squarespace tab, hard-refresh. You should see a **magenta inset frame** on the viewport. Remove the probe URL when done.

3. **If the probe works but CTAs do not change** — selectors in `cta-test-1.css` do not match your template. In DevTools, inspect a CTA, note its classes/tag, and add a matching selector (or share the outer HTML with your engineer).

Raw URL for the probe (after push):  
`https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/inject-probe.css`

### Magenta probe does not show (on Squarespace)

That usually means **the CSS never applies to the page** — not a CTA selector issue.

1. **Confirm the file loads** — Paste the probe raw URL into the address bar; you should see CSS text. If not, push `inject-probe.css` to `main` or fix the URL.
2. **Extension active on this tab** — Super CSS Inject popup: pick the probe (or CTA) stylesheet for **this** tab, then hard-refresh.
3. **CSP blocking external stylesheets** — Open DevTools → **Console** and look for messages like “Refused to load the stylesheet” / “Content Security Policy”. If present, URL-based injectors may not work on that site; use an extension that injects **inline** rules (e.g. [Stylus](https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne) or “User JavaScript and CSS”) and paste the contents of `cta-test-1.css` for your domain.
4. **Log CSP from your live URL** (helps narrow this down):

   `CHECK_PAGE_URL=https://your-published-site.com python3 scripts/verify_remote_stylesheet.py`

   Then read `.cursor/debug-d54107.log` for `hypothesisId` **H4** lines (`csp_headers` / `csp_fetch_failed`).

5. **Control test without Squarespace** — Open [`debug/local-probe.html`](../debug/local-probe.html) in Chrome. You should always see a **green top bar** (inline in the HTML). **Magenta inset** comes from CSS. If you see green but no magenta while using `file://`, Chrome may block linked styles; from the **repo root** run `python3 -m http.server 8765` and open `http://localhost:8765/debug/local-probe.html` instead.
