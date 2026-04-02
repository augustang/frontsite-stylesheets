# Squarespace overrides (Super CSS Inject)

Add these URLs in [Super CSS Inject](https://chromewebstore.google.com/detail/super-css-inject/pcfpmmmjdgngeidaggcahhoncahmpiin) → **Options** → stylesheet list. Use a short **alias** in the extension so the popup stays readable.

**CDN reality:** Both **jsDelivr `@main`** and **raw GitHub `.../main/...`** can be **temporarily out of sync** with each other or with your latest `git push` (either one may lag). For predictable DevTools behavior, **pin URLs to a commit SHA** (see below).

---

## Pin to commit (recommended)

After you **push**, point the extension at that exact commit so CDNs serve an immutable tree:

- **jsDelivr:**  
  `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@<SHA>/squarespace/<file>.css`  
  Use at least **7 characters** of the SHA; full 40-character SHA is fine.

- **Raw GitHub:**  
  `https://raw.githubusercontent.com/augustang/frontsite-stylesheets/<SHA>/squarespace/<file>.css`  
  Prefer the **full SHA** for raw.

**Super CSS Inject:** Each URL you want loaded must appear in **Options**. If you only add jsDelivr, **raw is never requested**—add both entries if you want to switch in the popup, and **select** the active stylesheet **per tab**. Raw will not “replace” jsDelivr unless you choose it.

**Helper:** From the repo root, run:

`python3 scripts/print_stylesheet_urls.py`

It prints paste-ready jsDelivr and raw lines for the current `HEAD` (after `git push`, run again and update the extension).

---

## Convenience: `@main` / `main` (may lag)

These track branch tips; after a push, wait for CDNs to refresh or use **pin to commit** above if DevTools still shows old CSS.

| Alias idea | jsDelivr `@main` |
| ---------- | ---------------- |
| CTA test 1 | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/cta-test-1.css` |
| Header v1  | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/header-v1.css` |
| Inject probe | `https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/inject-probe.css` |

Raw equivalent (also may lag on `/main/`):

`https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/<file>.css`

Hard-refresh the Squarespace tab after CDN updates.

---

## Workflow

1. Edit a `.css` file in this folder.
2. Commit and **push** to `origin`.
3. Run `python3 scripts/print_stylesheet_urls.py`, copy the **SHA-pinned** URLs into Super CSS Inject (or wait if you stay on `@main`).
4. Reload the page (or use the extension’s refresh behavior).

## More “sets”

Duplicate a file, rename it (e.g. `typography-tweaks.css`), push, and add URLs (pinned or `@main`) as new extension entries. Extend `print_stylesheet_urls.py` or build URLs by hand using the same patterns.

---

## Troubleshooting (injection vs selectors)

### Stylesheets in DevTools look out of date

- Run `python3 scripts/print_stylesheet_urls.py` after push and **update** the extension URLs to the new **SHA** (or retry after CDN delay if using `@main`).
- Run `python3 scripts/verify_remote_stylesheet.py` and read `.cursor/debug-d54107.log`: **H3** `local_vs_default_url` vs **H3** `local_vs_raw_github_main` shows jsDelivr vs raw mismatch against your disk.

### Raw URL not injected (only jsDelivr loads)

1. **Registered?** Super CSS Inject **Options** must include the **raw** URL as its own entry; the popup must **select** it for that tab if you want raw active.
2. **Valid URL?** Paste it in the address bar—you should see **CSS source**, not an HTML GitHub page. Use `raw.githubusercontent.com`, not `github.com/.../blob/...`.
3. **Network:** DevTools → **Network** → filter **CSS** → hard refresh. Look for `raw.githubusercontent.com`: **missing** = extension not using that URL; **failed / blocked** = check **Console** for CSP blocking `raw.githubusercontent.com`.

### Other

1. **Probe works but CTAs do not change** — In the extension **popup**, switch the active sheet from **inject-probe** to **cta-test-1** (or enable both if supported). Probe rules are not CTA rules.

2. **Verify script (optional)** — `python3 scripts/verify_remote_stylesheet.py` appends lines to `.cursor/debug-d54107.log` (H1–H6: fetch checks, jsDelivr vs raw probe compare, optional CSP). See earlier bullets for **H3** / **H5** / **H6**.

   `CHECK_PAGE_URL=https://yoursite.com python3 scripts/verify_remote_stylesheet.py`

3. **Still no CTA change with `cta-test-1.css` active** — Inspect a button in DevTools, add selectors to `cta-test-1.css`, commit, push, update pinned URLs, hard-refresh.

### Magenta probe does not show (on Squarespace)

1. Paste the probe URL in the address bar; you should see CSS text.
2. Extension popup: pick that stylesheet for **this** tab; hard-refresh.
3. **CSP** — Console messages about refusing stylesheets → try **pin SHA** URLs, or inline injectors (e.g. [Stylus](https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne)).
4. `CHECK_PAGE_URL=https://your-published-site.com python3 scripts/verify_remote_stylesheet.py` then read log **H4** for CSP headers.
5. **Local control:** [`debug/local-probe.html`](../debug/local-probe.html) or `python3 -m http.server` from repo root → `http://localhost:8765/debug/local-probe.html`.
