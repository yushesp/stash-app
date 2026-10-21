"""Builds the Stash site: python3 build.py. Pages live in _src as HTML bodies; this
wraps each in the shared head, header and footer and writes <page>/index.html."""
import pathlib, re

ROOT = pathlib.Path(__file__).parent
SUPPORT_EMAIL = "apps@yushes.com"
PAGES = {"index": ("Stash", ""), "privacy": ("Privacy Policy", "privacy"),
         "terms": ("Terms of Use", "terms"), "support": ("Support", "support"),
         "leaving-ynab": ("Leaving YNAB?", "leaving-ynab")}

def nav(current):
    links = [("support", "Support"), ("privacy", "Privacy"), ("terms", "Terms")]
    return "".join(f'<a href="/stash-app/{p}/"{" aria-current=page" if p == current else ""}>{t}</a>' for p, t in links)

def page(name, title, path, body):
    hero = name == "index"
    head = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title if hero else f"{title} | Stash"}</title>
<meta name="description" content="Stash is a simple envelope budget for iPhone. Give every dollar a home.">
<link rel="icon" href="/stash-app/favicon.png"><link rel="apple-touch-icon" href="/stash-app/favicon.png">
<link rel="stylesheet" href="/stash-app/style.css">
</head><body>"""
    header = f"""<header class="site"><img src="/stash-app/icon.png" alt=""><a href="/stash-app/">Stash</a><nav>{nav(path)}</nav></header>"""
    footer = f"""<footer><span>© 2026 Stash</span><a href="/stash-app/support/">Support</a><a href="/stash-app/privacy/">Privacy</a><a href="/stash-app/terms/">Terms</a><a href="/stash-app/leaving-ynab/">Leaving YNAB?</a><a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></footer>"""
    if hero:
        top, rest = body.split("<!-- /hero -->")
        return f"""{head}<div class="hero"><div class="wrap">{header}{top}</div></div><main class="wrap">{rest}{footer}</main></body></html>\n"""
    return f"""{head}<main class="wrap">{header}{body}{footer}</main></body></html>\n"""

for name, (title, path) in PAGES.items():
    body = (ROOT / "_src" / f"{name}.html").read_text().replace("SUPPORT_EMAIL", SUPPORT_EMAIL)
    out = ROOT / (path or ".") / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page(name, title, path, body))
    print("wrote", out.relative_to(ROOT))
