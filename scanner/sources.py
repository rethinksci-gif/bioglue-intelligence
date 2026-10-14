"""Discovery: Crossref works search and date-bounded Google News RSS. Discovery is not evidence."""
from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime

from .config import config

UA = "BIOGLUE-Intelligence/0.1 (+https://github.com/rethinksci-gif/bioglue-intelligence)"


def _get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _clean(text: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return " ".join(html.unescape(text).split())


def _date(parts) -> str | None:
    try:
        p = parts["date-parts"][0]
        return date(p[0], p[1] if len(p) > 1 else 1, p[2] if len(p) > 2 else 1).isoformat(), len(p) == 3
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def crossref(query: str, start: date, end: date, rows: int) -> list[dict]:
    params = {
        "query.bibliographic": query,
        "filter": f"from-pub-date:{start},until-pub-date:{end},type:journal-article",
        "rows": rows,
        "select": "DOI,title,author,container-title,published-online,published-print,issued,abstract,URL,publisher",
        "mailto": config()["scan"]["mailto"],
    }
    data = json.loads(_get("https://api.crossref.org/works?" + urllib.parse.urlencode(params)))
    out = []
    for m in data["message"]["items"]:
        if not m.get("title"):
            continue
        dated = _date(m.get("published-online")) or _date(m.get("published-print")) or _date(m.get("issued"))
        if not dated:
            continue
        published, exact = dated
        # Crossref filters on any of its dates; keep only items whose first date is inside the window.
        if not (start.isoformat() <= published <= end.isoformat()):
            continue
        authors = m.get("author") or []
        out.append({
            "id": "doi:" + m["DOI"].lower(),
            "kind": "literature",
            "title": _clean(m["title"][0]),
            "abstract": _clean(m.get("abstract")),
            "venue": _clean((m.get("container-title") or [""])[0]),
            "publisher": m.get("publisher", ""),
            "authors": ", ".join(a.get("family", "") for a in authors[:3]) + (" et al." if len(authors) > 3 else ""),
            "date": published,
            "date_precision": "day" if exact else "month",
            "url": "https://doi.org/" + m["DOI"],
            "query": query,
        })
    return out


def news(query: str, start: date, end: date, limit: int) -> list[dict]:
    q = f"{query} after:{start - timedelta(days=1)} before:{end + timedelta(days=1)}"
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})
    root = ET.fromstring(_get(url))
    out = []
    for item in root.iter("item"):
        try:
            when = parsedate_to_datetime(item.findtext("pubDate")).date()
        except (TypeError, ValueError):
            continue
        if not start <= when <= end:
            continue
        title = _clean(item.findtext("title"))
        link = item.findtext("link") or ""
        out.append({
            "id": "news:" + hashlib.sha1(title.casefold().encode()).hexdigest()[:16],
            "kind": "news",
            "title": title,
            "abstract": _clean(item.findtext("description")),
            "venue": _clean(item.findtext("source")),
            "publisher": "",
            "authors": "",
            "date": when.isoformat(),
            "date_precision": "day",
            "url": link,
            "query": query,
        })
        if len(out) >= limit:
            break
    return out


def discover(routes: list[dict], start: date, end: date, log=print) -> list[dict]:
    cfg = config()["scan"]
    seen: dict[str, dict] = {}
    for route in routes:
        for kind, fn, n in (("crossref", crossref, cfg["crossref_rows"]), ("news", news, cfg["news_items"])):
            for query in route["scan"].get(kind, []):
                try:
                    items = fn(query, start, end, n)
                except Exception as exc:  # network failures are logged, never fatal
                    log(f"  ! {kind} '{query}': {exc}")
                    continue
                log(f"  {kind:8} {route['id']:16} {len(items):3}  {query}")
                for it in items:
                    entry = seen.setdefault(it["id"], {**it, "seed_routes": []})
                    if route["id"] not in entry["seed_routes"]:
                        entry["seed_routes"].append(route["id"])
    return sorted(seen.values(), key=lambda x: (x["date"], x["id"]))
