"""Builds the Stash site: python3 build.py. Pages live in _src as HTML bodies; this
wraps each in the shared head, header and footer and writes <page>/index.html.
It also writes sitemap.xml and llms.txt, and the FAQ page's structured data."""
import datetime, html, json, pathlib, re

ROOT = pathlib.Path(__file__).parent
BASE = "https://yushesp.github.io/stash-app/"
SUPPORT_EMAIL = "apps@yushes.com"
APP_ID = "6824625025"
APP_STORE = f"https://apps.apple.com/us/app/stash-see-your-money-move/id{APP_ID}"
NAME = "Stash: See Your Money Move"

# name: (title, path, description)
PAGES = {
    "index": (f"{NAME} | Envelope budget and retirement calculator for iPhone", "",
              "Stash is an envelope budget for iPhone that logs your spending from bank alerts and shows the year you could retire. "
              "Zero-based, no bank login, your data stays in your iCloud. The whole budget is free."),
    "faq": ("Questions about Stash", "faq",
            "Answers about Stash, the iPhone envelope budget: how auto-log works, the retirement year, YNAB import, privacy, currencies and price."),
    "compare": ("Stash vs YNAB, Goodbudget and EveryDollar", "compare",
                "How Stash compares with YNAB, Goodbudget and EveryDollar: price, bank login, auto-logging and the retirement year."),
    "leaving-ynab": ("Leaving YNAB? Move your budget to Stash", "leaving-ynab",
                     "Move your YNAB budget to Stash in about a minute: export your plan from YNAB and open it in Stash on your iPhone."),
    "support": ("Support", "support", "Help with Stash, the iPhone envelope budget."),
    "privacy": ("Privacy Policy", "privacy", "How Stash handles your data."),
    "terms": ("Terms of Use", "terms", "Terms of use for Stash."),
}
SITEMAP = ["index", "faq", "compare", "leaving-ynab", "support", "privacy", "terms"]

APP_LD = {
    "@context": "https://schema.org", "@type": "MobileApplication",
    "name": NAME, "alternateName": ["Stash budget app", "Stash envelope budget"],
    "operatingSystem": "iOS 18 or later", "applicationCategory": "FinanceApplication",
    "description": PAGES["index"][2], "url": BASE, "downloadUrl": APP_STORE,
    "installUrl": APP_STORE, "image": BASE + "icon.png",
    "author": {"@type": "Person", "name": "Prathyush Shankar"},
    "offers": [
        {"@type": "Offer", "name": "Stash (free)", "price": "0", "priceCurrency": "USD"},
        {"@type": "Offer", "name": "Stash Plus monthly", "price": "0.99", "priceCurrency": "USD"},
        {"@type": "Offer", "name": "Stash Plus yearly", "price": "9.99", "priceCurrency": "USD"},
        {"@type": "Offer", "name": "Stash Plus lifetime", "price": "49.99", "priceCurrency": "USD"},
    ],
    "featureList": ["Zero-based envelope budget", "Auto-log spending from bank alerts and Apple Pay",
                    "Retirement year estimate", "Credit card payment envelopes", "Import from YNAB",
                    "Bank screenshot import", "Siri and Shortcuts", "35 currencies", "No bank login"],
}

def nav(current):
    links = [("faq", "FAQ"), ("compare", "Compare"), ("support", "Support")]
    return "".join(f'<a href="/stash-app/{p}/"{" aria-current=page" if p == current else ""}>{t}</a>' for p, t in links)

def faq_ld(body):
    qa = re.findall(r"<h2[^>]*>(.*?)</h2>\s*(.*?)(?=<h2|<section|\Z)", body, re.S)
    strip = lambda s: " ".join(html.unescape(re.sub(r"<[^>]+>", "", s)).split())
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qa if strip(a)]}

def page(name, body):
    title, path, desc = PAGES[name]
    hero = name == "index"
    url = BASE + (f"{path}/" if path else "")
    lds = [APP_LD] if hero else []
    if name == "faq": lds.append(faq_ld(body))
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    full_title = title if hero else f"{title} | Stash"
    head = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="apple-itunes-app" content="app-id={APP_ID}">
<meta property="og:type" content="website"><meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}img/3-retire.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/stash-app/favicon.png"><link rel="apple-touch-icon" href="/stash-app/favicon.png">
<link rel="stylesheet" href="/stash-app/style.css">{ld}
</head><body>"""
    header = f"""<header class="site"><img src="/stash-app/icon.png" alt=""><a href="/stash-app/">Stash</a><nav>{nav(path)}</nav></header>"""
    footer = f"""<footer><span>© 2026 Stash</span><a href="{APP_STORE}">App Store</a><a href="/stash-app/faq/">FAQ</a><a href="/stash-app/compare/">Compare</a><a href="/stash-app/leaving-ynab/">Leaving YNAB?</a><a href="/stash-app/support/">Support</a><a href="/stash-app/privacy/">Privacy</a><a href="/stash-app/terms/">Terms</a><a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></footer>"""
    if hero:
        top, rest = body.split("<!-- /hero -->")
        return f"""{head}<div class="hero"><div class="wrap">{header}{top}</div></div><main class="wrap">{rest}{footer}</main></body></html>\n"""
    return f"""{head}<main class="wrap">{header}{body}{footer}</main></body></html>\n"""

def fill(s):
    return s.replace("SUPPORT_EMAIL", SUPPORT_EMAIL).replace("APP_STORE_URL", APP_STORE)

for name, (title, path, desc) in PAGES.items():
    body = fill((ROOT / "_src" / f"{name}.html").read_text())
    out = ROOT / (path or ".") / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page(name, body))
    print("wrote", out.relative_to(ROOT))

today = datetime.date.today().isoformat()
urls = "".join(f"<url><loc>{BASE}{(PAGES[n][1] + '/') if PAGES[n][1] else ''}</loc><lastmod>{today}</lastmod></url>" for n in SITEMAP)
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
(ROOT / "llms.txt").write_text(fill((ROOT / "_src" / "llms.txt").read_text()))
print("wrote sitemap.xml, llms.txt")
