#!/usr/bin/env python3
# region agent log
"""Append NDJSON lines to debug log to test H1–H3 for hosted CSS."""
# endregion
import json
import os
import ssl
import time
import urllib.error
import urllib.request

LOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", ".cursor", "debug-d54107.log"
)
LOG_PATH = os.path.normpath(LOG_PATH)
SESSION_ID = "d54107"
DEFAULT_URL = (
    "https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/"
    "squarespace/cta-test-1.css"
)


def emit(hypothesis_id: str, message: str, data: dict, run_id: str = "verify") -> None:
    line = {
        "sessionId": SESSION_ID,
        "hypothesisId": hypothesis_id,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
        "location": "scripts/verify_remote_stylesheet.py",
        "runId": run_id,
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def _fetch_text(url: str) -> tuple[int | None, str, str | None]:
    """HTTP GET url; return (status, body, error_message). error_message set on failure."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "frontsite-stylesheets-verify/1.0"},
    )

    def open_url(ctx: ssl.SSLContext | None):
        kw: dict = {"timeout": 25}
        if ctx is not None:
            kw["context"] = ctx
        return urllib.request.urlopen(req, **kw)

    try:
        try:
            with open_url(ssl.create_default_context()) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace"), None
        except Exception as e1:
            err = str(e1)
            if "CERTIFICATE_VERIFY_FAILED" in err or "SSL" in type(e1).__name__:
                with open_url(ssl._create_unverified_context()) as resp:
                    return resp.status, resp.read().decode("utf-8", errors="replace"), None
            raise
    except Exception as e:
        return None, "", f"{type(e).__name__}: {e}"[:500]


def main() -> None:
    url = os.environ.get("VERIFY_STYLESHEET_URL", DEFAULT_URL)
    emit("H1", "fetch_start", {"url": url}, run_id="verify")

    body = ""
    status = 0
    content_type = ""

    def do_fetch(ctx: ssl.SSLContext | None) -> tuple[int, str, str]:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "frontsite-stylesheets-verify/1.0"},
        )
        kwargs = {"timeout": 25}
        if ctx is not None:
            kwargs["context"] = ctx
        with urllib.request.urlopen(req, **kwargs) as resp:
            st = resp.status
            ct = resp.headers.get("Content-Type", "")
            bd = resp.read().decode("utf-8", errors="replace")
        return st, ct, bd

    try:
        status, content_type, body = do_fetch(ssl.create_default_context())
    except urllib.error.HTTPError as e:
        emit(
            "H1",
            "fetch_http_error",
            {"status": e.code, "url": url},
            run_id="verify",
        )
        return
    except Exception as e:
        err = str(e)
        if "CERTIFICATE_VERIFY_FAILED" in err or "SSL" in type(e).__name__:
            emit(
                "H1",
                "fetch_ssl_retry_unverified",
                {
                    "note": "Python SSL certs missing in this environment; retrying once for verify script only",
                    "error": type(e).__name__,
                },
                run_id="verify",
            )
            try:
                status, content_type, body = do_fetch(ssl._create_unverified_context())
            except Exception as e2:
                emit(
                    "H1",
                    "fetch_exception",
                    {
                        "error": type(e2).__name__,
                        "detail": str(e2)[:500],
                        "url": url,
                    },
                    run_id="verify",
                )
                return
        else:
            emit(
                "H1",
                "fetch_exception",
                {"error": type(e).__name__, "detail": err[:500], "url": url},
                run_id="verify",
            )
            return

    emit(
        "H1",
        "fetch_ok",
        {
            "status": status,
            "contentType": content_type,
            "byteLength": len(body.encode("utf-8")),
            "url": url,
        },
        run_id="verify",
    )

    has_rule = "border-radius" in body and "4px" in body
    has_sqs = "sqs-" in body
    emit(
        "H2",
        "body_checks",
        {
            "hasBorderRadius4px": has_rule,
            "hasSqsSelectors": has_sqs,
            "preview": body[:240].replace("\n", "\\n"),
        },
        run_id="verify",
    )

    local = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "squarespace", "cta-test-1.css")
    )
    try:
        with open(local, encoding="utf-8") as f:
            local_body = f.read()
        lb = local_body.strip()
        emit(
            "H3",
            "local_vs_default_url",
            {
                "localPath": local,
                "comparedToUrl": url,
                "exactMatch": lb == body.strip(),
                "remoteBytes": len(body.encode("utf-8")),
                "localBytes": len(local_body.encode("utf-8")),
                "note": "Compared to VERIFY_STYLESHEET_URL or DEFAULT_URL (often jsDelivr)",
            },
            run_id="verify",
        )
        # jsDelivr can lag GitHub after a push; compare the same file on raw /main/ too.
        raw_cta = (
            "https://raw.githubusercontent.com/augustang/frontsite-stylesheets/"
            "main/squarespace/cta-test-1.css"
        )
        if local.endswith("cta-test-1.css"):
            _st_r, body_r, err_r = _fetch_text(raw_cta)
            if err_r:
                emit(
                    "H3",
                    "local_vs_raw_github_failed",
                    {"url": raw_cta, "error": err_r},
                    run_id="verify",
                )
            else:
                emit(
                    "H3",
                    "local_vs_raw_github_main",
                    {
                        "localPath": local,
                        "comparedToUrl": raw_cta,
                        "exactMatch": lb == body_r.strip(),
                        "remoteBytes": len(body_r.encode("utf-8")),
                        "localBytes": len(local_body.encode("utf-8")),
                        "note": "If true but local_vs_default_url is false, jsDelivr is stale; wait or use raw URL in extension",
                    },
                    run_id="verify",
                )
    except OSError as e:
        emit("H3", "local_read_failed", {"error": str(e)}, run_id="verify")

    log_inject_probe_cdns()

    # H4: page CSP may block <link href="https://raw.githubusercontent.com/...">
    page_url = os.environ.get("CHECK_PAGE_URL", "").strip()
    urls: list[tuple[str, str]] = []
    if page_url:
        urls.append((page_url, "user_site"))
    if os.environ.get("CHECK_SQUARESPACE_REFERENCE", "1") not in ("0", "false", "no"):
        urls.append(("https://www.squarespace.com/", "squarespace_com_reference"))

    if not urls:
        emit(
            "H4",
            "csp_skip",
            {
                "reason": "Set CHECK_PAGE_URL to your live site to log its CSP, or leave default reference on",
            },
            run_id="verify",
        )
    for u, label in urls:
        log_csp_headers(u, label)


def log_inject_probe_cdns() -> None:
    # region agent log
    """H5 jsDelivr (recommended CDN); H6 raw /main staleness vs jsDelivr."""
    override = os.environ.get("VERIFY_INJECT_PROBE_URL", "").strip()
    jsd_url = "https://cdn.jsdelivr.net/gh/augustang/frontsite-stylesheets@main/squarespace/inject-probe.css"
    raw_url = "https://raw.githubusercontent.com/augustang/frontsite-stylesheets/main/squarespace/inject-probe.css"

    if override:
        emit("H5", "inject_probe_check_start", {"url": override}, run_id="verify")
        st, body, err = _fetch_text(override)
        if err:
            emit(
                "H5",
                "inject_probe_fetch_failed",
                {"error": err, "url": override},
                run_id="verify",
            )
            return
        low = body.lower()
        emit(
            "H5",
            "inject_probe_fetch_ok",
            {
                "cdn": "override",
                "status": st,
                "byteLength": len(body.encode("utf-8")),
                "containsMagentaToken": "ff00ff" in low,
                "containsBodyBeforeOverlay": "body::before" in low,
            },
            run_id="verify",
        )
        return

    emit("H5", "inject_probe_jsdelivr_start", {"url": jsd_url}, run_id="verify")
    st_j, body_j, err_j = _fetch_text(jsd_url)
    if err_j:
        emit(
            "H5",
            "inject_probe_jsdelivr_failed",
            {"error": err_j, "url": jsd_url},
            run_id="verify",
        )
    else:
        low_j = body_j.lower()
        emit(
            "H5",
            "inject_probe_jsdelivr_ok",
            {
                "status": st_j,
                "byteLength": len(body_j.encode("utf-8")),
                "containsMagentaToken": "ff00ff" in low_j,
                "containsBodyBeforeOverlay": "body::before" in low_j,
            },
            run_id="verify",
        )

    emit("H6", "inject_probe_raw_main_start", {"url": raw_url}, run_id="verify")
    st_r, body_r, err_r = _fetch_text(raw_url)
    if err_r:
        emit(
            "H6",
            "inject_probe_raw_main_failed",
            {"error": err_r, "url": raw_url},
            run_id="verify",
        )
        return

    low_r = body_r.lower()
    match_jsd = err_j is None and body_r == body_j
    emit(
        "H6",
        "inject_probe_raw_main_ok",
        {
            "status": st_r,
            "byteLength": len(body_r.encode("utf-8")),
            "containsMagentaToken": "ff00ff" in low_r,
            "containsBodyBeforeOverlay": "body::before" in low_r,
            "bodyEqualsJsdelivrMain": match_jsd,
        },
        run_id="verify",
    )
    # endregion


def log_csp_headers(page_url: str, label: str) -> None:
    # region agent log
    emit("H4", "csp_fetch_start", {"pageUrl": page_url, "label": label}, run_id="verify")
    # endregion

    def try_open(ctx: ssl.SSLContext | None):
        req = urllib.request.Request(
            page_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
            },
        )
        kw: dict = {"timeout": 25}
        if ctx is not None:
            kw["context"] = ctx
        return urllib.request.urlopen(req, **kw)

    resp = None
    try:
        try:
            resp = try_open(ssl.create_default_context())
        except Exception as e:
            err = str(e)
            if "CERTIFICATE_VERIFY_FAILED" in err or "SSL" in type(e).__name__:
                resp = try_open(ssl._create_unverified_context())
            else:
                raise
        status = resp.status
        csp = resp.headers.get("Content-Security-Policy", "") or ""
        csp_ro = resp.headers.get("Content-Security-Policy-Report-Only", "") or ""
        try:
            resp.read(8192)
        except Exception:
            pass
        resp.close()
        combined = (csp + " " + csp_ro).lower()
        mentions_github = "raw.githubusercontent.com" in combined
        mentions_style_src = "style-src" in combined
        emit(
            "H4",
            "csp_headers",
            {
                "label": label,
                "pageUrl": page_url,
                "httpStatus": status,
                "cspLength": len(csp),
                "cspReportOnlyLength": len(csp_ro),
                "cspTruncated": (csp[:1800] if csp else ""),
                "mentionsRawGithub": mentions_github,
                "hasStyleSrcDirective": mentions_style_src,
            },
            run_id="verify",
        )
    except Exception as e:
        emit(
            "H4",
            "csp_fetch_failed",
            {
                "label": label,
                "pageUrl": page_url,
                "error": type(e).__name__,
                "detail": str(e)[:500],
            },
            run_id="verify",
        )


if __name__ == "__main__":
    main()
