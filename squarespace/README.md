# Squarespace overrides

Test custom CSS on your Squarespace site without losing work when you close DevTools. This repo is the **source of truth**; you apply it in the browser in one of two ways:

1. **[Stylebot](https://stylebot.dev/)** (recommended when URL-based injection is flaky) — paste CSS directly; no GitHub CDN or raw URL required. See [Stylebot help](https://stylebot.dev/help/).
2. **Hosted stylesheet + [Super CSS Inject](https://chromewebstore.google.com/detail/super-css-inject/pcfpmmmjdgngeidaggcahhoncahmpiin)** — point the extension at a public URL (jsDelivr / raw GitHub). Good when you want the extension to pull updates after every push.

Primary stylesheet for experiments: [`cta-test-1.css`](cta-test-1.css).

---

## Option A: Stylebot

[Stylebot](https://stylebot.dev/help/) injects **custom CSS in the page** via its **Code editor** (or Options). You avoid external stylesheet URLs, CDN lag between jsDelivr and GitHub, and many CSP issues that block `<link href="…">` injectors.

### Setup

1. Install **Stylebot** for your browser from [stylebot.dev](https://stylebot.dev/) (or your browser’s extension store).
2. Open your **live or preview** Squarespace URL.
3. Launch Stylebot from the toolbar icon or **Alt+Shift+M** (shortcut is customizable; see [Launching Stylebot](https://stylebot.dev/help/)).
4. Open the **Code editor** and paste the **full contents** of [`cta-test-1.css`](cta-test-1.css) (or a trimmed subset once you know what you need). Styles save automatically for that site’s URL rule.

### URL matching

By default Stylebot matches your **site’s domain**. If you use both a **custom domain** and a `*.squarespace.com` preview URL, configure patterns under Options so the same rules apply everywhere you test. See [URL syntax rules](https://stylebot.dev/help/) (wildcards `*` / `**`, comma-separated patterns, etc.).

### Inspect and selectors

Use Stylebot’s **Inspect** control to pick an element; it can suggest a selector. You can also type your own in the **CSS selector** field to highlight matches—useful for tuning `.global-navigation__cta` and `.cta--primary`. Note: [hash-based class names](https://stylebot.dev/help/) can change when the site updates; prefer stable classes when possible.

### Sync and backup

Optional: enable **Sync via Google Drive** in Stylebot Options, or **export / import** styles as JSON so you are not tied to a single browser profile. Details: [Sync and Backup](https://stylebot.dev/help/).

---

## Option B: Hosted stylesheet (Super CSS Inject)

Add these URLs in [Super CSS Inject](https://chromewebstore.google.com/detail/super-css-inject/pcfpmmmjdgngeidaggcahhoncahmpiin) → **Options** → stylesheet list. Use a short **alias** in the extension so the popup stays readable.

**Use jsDelivr URLs below** — `raw.githubusercontent.com/.../main/...` can lag behind `main` on the CDN (we saw `inject-probe.css` stale on raw while `main` was correct). jsDelivr `@main` usually tracked the repo tip, but it can lag too; the verify script compares both.

Replace `main` in the path with a **commit SHA** (e.g. `@df60b9d`) if you need a frozen revision.

### Stylesheet URLs (copy-paste)

| Alias idea | URL (jsDelivr `@main`) |
| ---------- | ---------------------- |
| CTA test 1 | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/cta-test-1.css` |
| Header v1  | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/header-v1.css` |
| Inject probe | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/inject-probe.css` |

Equivalent raw GitHub (may be CDN-stale for some files):  
`https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/<file>.css`

After you **push** changes, allow a short delay for CDNs; hard-refresh the Squarespace tab if needed.

### More “sets” (hosted)

Duplicate a file, rename it (e.g. `typography-tweaks.css`), push, and add its jsDelivr URL as another entry in the extension.

---

## Workflow

1. Edit [`cta-test-1.css`](cta-test-1.css) (or other files) in this repo and **commit** so you have history and can share with your engineer.
2. **Stylebot:** paste the updated file into Stylebot’s code editor for your domain (and re-sync / export if you use backup).
3. **Super CSS Inject:** `git push origin main`, wait for CDNs if needed, ensure the correct sheet is active for the tab, then hard-refresh.

---

## Troubleshooting

If **hosted URLs** still misbehave (nothing applies, wrong version, CSP errors), use **Option A: Stylebot** above and paste [`cta-test-1.css`](cta-test-1.css) instead of fighting CDNs or injectors.

### Super CSS Inject and selectors

1. **Probe works but CTAs do not change** — In Super CSS Inject’s **popup for that tab**, switch the active stylesheet from **inject-probe** to **cta-test-1** (or enable both if the extension allows multiple injections). The probe only loads `inject-probe.css`; your button rules live in `cta-test-1.css`.

2. **Optional — “verify script” (what it does)**  
   From the repo folder in Terminal:

   `python3 scripts/verify_remote_stylesheet.py`

   That script **downloads** your public CSS from the internet (same URLs the extension uses) and appends lines to **`.cursor/debug-d54107.log`**. You do not need to read it unless you’re debugging hosting/CDN issues. In plain terms:
   - **H1 / H2** — `cta-test-1.css` returned 200 and contains `border-radius` / `sqs-` selectors.
   - **H3** — two lines when checking `cta-test-1.css`: **`local_vs_default_url`** compares your disk file to **jsDelivr** (can show `exactMatch: false` for a few minutes after `git push` while the CDN updates). **`local_vs_raw_github_main`** compares the same file to **raw GitHub** `/main/`; if that one is `exactMatch: true`, your push is fine and the extension will catch up once jsDelivr refreshes (or temporarily use the raw URL in Super CSS Inject).
   - **H5** — `inject-probe.css` on jsDelivr is the new overlay (`containsBodyBeforeOverlay: true`).
   - **H6** — whether **raw GitHub** `/main/` for the probe matches jsDelivr (`bodyEqualsJsdelivrMain`; `false` means raw was stale).

   To also log **Content-Security-Policy** headers for **your** live site:  
   `CHECK_PAGE_URL=https://yoursite.com python3 scripts/verify_remote_stylesheet.py`

3. **Still no CTA change with `cta-test-1.css` active** — In DevTools, **inspect** a button, note the tag and `class` values on the clickable node (and its parent), then add matching selectors to `cta-test-1.css`, commit, push (or paste into Stylebot), and hard-refresh.

### Magenta probe does not show (on Squarespace)

That usually means **the CSS never applies to the page** — not a CTA selector issue.

1. **Confirm the file loads** — Paste the probe URL into the address bar; you should see CSS text.
2. **Extension active on this tab** — Super CSS Inject popup: pick the probe (or CTA) stylesheet for **this** tab, then hard-refresh.
3. **CSP blocking external stylesheets** — Open DevTools → **Console** and look for messages like “Refused to load the stylesheet” / “Content Security Policy”. If present, prefer **[Stylebot](https://stylebot.dev/help/)** (paste `cta-test-1.css`) or [Stylus](https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne) / “User JavaScript and CSS” with inline rules for your domain.
4. **Log CSP from your live URL** (helps narrow this down):

   `CHECK_PAGE_URL=https://your-published-site.com python3 scripts/verify_remote_stylesheet.py`

   Then read `.cursor/debug-d54107.log` for **H4** lines (`csp_headers` / `csp_fetch_failed`).

5. **Control test without Squarespace** — Open [`debug/local-probe.html`](../debug/local-probe.html) in Chrome. You should always see a **green top bar** (inline in the HTML). **Magenta inset** comes from CSS. If you see green but no magenta while using `file://`, Chrome may block linked styles; from the **repo root** run `python3 -m http.server 8765` and open `http://localhost:8765/debug/local-probe.html` instead.
