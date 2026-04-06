"""PPE.pl metadata scraper plugin for GamesDownloader V3.

Searches DuckDuckGo/Bing for game pages on ppe.pl, then scrapes:
- Polish description
- Rating (0-10 scale)
- Genre
- Release date
- Developer
- Screenshots gallery
- Cover image
"""

from __future__ import annotations

import logging
import re
import threading
import unicodedata as _uc
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from plugins.hookspecs import hookimpl

logger = logging.getLogger("plugin.ppe-metadata")

# -- Regex patterns --
_IMG_EXT = re.compile(r"\.(?:jpe?g|png|webp|gif)(?:\?.*)?$", re.IGNORECASE)
_DATE_RE = re.compile(r"^\d{1,2}\.\d{1,2}\.\d{4}$")
_GAME_URL_RE = re.compile(
    r"^https?://(www\.)?ppe\.pl/gry/[^/]+(/\d+)?/?$", re.IGNORECASE
)
_HDRS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
}

_local = threading.local()
MIN_MATCH = 0.65


# -- Text utilities --

def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _canon(s: str) -> str:
    nfkd = _uc.normalize("NFKD", s)
    s = "".join(c for c in nfkd if not _uc.combining(c)).lower()
    s = re.sub(r"[''`]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return _ws(s)


def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, _canon(a), _canon(b)).ratio()


def _lines(soup) -> list[str]:
    text = soup.get_text("\n", strip=True)
    lines = [_ws(x) for x in text.splitlines()]
    return [x for x in lines if x]


# -- HTTP client --

def _client() -> httpx.Client:
    c = getattr(_local, "client", None)
    if c is None:
        c = httpx.Client(headers=_HDRS, timeout=20, follow_redirects=True)
        _local.client = c
    return c


def _get(url: str, **kw) -> httpx.Response:
    try:
        return _client().get(url, **kw)
    except Exception:
        _local.client = None
        return httpx.Client(headers=_HDRS, timeout=20, follow_redirects=True).get(url, **kw)


# -- Search --

def _ddg_search(title: str, max_results: int = 15) -> list[dict]:
    q = quote_plus(f"site:ppe.pl/gry/ {title}")
    url = f"https://duckduckgo.com/html/?q={q}"
    try:
        r = _get(url)
        if r.status_code not in (200, 202):
            return []
        # CAPTCHA detection - DDG shows anomaly modal when rate-limited
        if "anomaly-modal" in r.text or "challenge-form" in r.text:
            logger.info("DDG CAPTCHA detected for '%s', falling back to Bing", title)
            return _bing_search(title, max_results)
        soup = BeautifulSoup(r.text, "html.parser")
        out: list[dict] = []
        seen: set[str] = set()
        for res in soup.select("div.result"):
            a = res.select_one("a.result__a")
            if not a or not a.get("href"):
                continue
            href = _unwrap_ddg(a["href"]).split("?")[0].rstrip("/")
            if not _GAME_URL_RE.match(href) or href in seen:
                continue
            seen.add(href)
            name = _ws(a.get_text(" ", strip=True))
            snip = res.select_one(".result__snippet")
            snippet = _ws(snip.get_text(" ", strip=True)) if snip else ""
            out.append({"name": name, "url": href, "snippet": snippet})
            if len(out) >= max_results:
                break
        # Fallback: all links
        if not out:
            for a in soup.find_all("a", href=True):
                href = _unwrap_ddg(a["href"]).split("?")[0].rstrip("/")
                if not _GAME_URL_RE.match(href) or href in seen:
                    continue
                seen.add(href)
                slug = href.rstrip("/").split("/")[-1]
                out.append({"name": re.sub(r"[-_]+", " ", slug), "url": href, "snippet": ""})
                if len(out) >= max_results:
                    break
        return out
    except Exception as e:
        logger.debug("DDG search error: %s", e)
        return _bing_search(title, max_results)


def _bing_search(title: str, max_results: int = 15) -> list[dict]:
    q = quote_plus(f"site:ppe.pl/gry {title}")
    url = f"https://www.bing.com/search?q={q}&count=20&setlang=pl-PL"
    hdrs = {**_HDRS, "Cookie": "SRCHHPGUSR=SRCHLANG=pl; SRCHD=AF=NOFORM"}
    try:
        r = httpx.get(url, headers=hdrs, timeout=15, follow_redirects=True)
        soup = BeautifulSoup(r.text, "html.parser")
        out: list[dict] = []
        seen: set[str] = set()
        for a in soup.select("li.b_algo h2 a"):
            href = (a.get("href") or "").strip().split("?")[0].rstrip("/")
            if not _GAME_URL_RE.match(href) or href in seen:
                continue
            seen.add(href)
            raw = _ws(a.get_text(" ", strip=True))
            name = re.sub(r"\s*[-]\s*PPE\.pl.*$", "", raw, flags=re.IGNORECASE).strip()
            li = a.find_parent("li")
            snip = li.select_one(".b_caption p") if li else None
            snippet = _ws(snip.get_text(" ", strip=True)) if snip else ""
            out.append({"name": name or href.split("/")[-1], "url": href, "snippet": snippet})
            if len(out) >= max_results:
                break
        return out
    except Exception as e:
        logger.debug("Bing search error: %s", e)
        return []


def _unwrap_ddg(href: str) -> str:
    if "uddg=" in href:
        m = re.search(r"uddg=([^&]+)", href)
        if m:
            from urllib.parse import unquote
            return unquote(m.group(1))
    return href.strip()


def _ppe_api_search(title: str, max_results: int = 15) -> list[dict]:
    """Search using PPE.pl native API: /api/search?search=...&type=game&page=0"""
    try:
        q = quote_plus(title)
        url = f"https://www.ppe.pl/api/search?search={q}&type=game&page=0"
        r = _get(url)
        if r.status_code != 200:
            return []
        data = r.json()
        html = data.get("result", "")
        if not html or "empty-results" in html:
            return []
        # Parse HTML results: <a href="/gry/Slug/ID" class="result">...<div class="result-caption"><div>Title</div>
        soup = BeautifulSoup(html, "html.parser")
        out: list[dict] = []
        for a in soup.select("a.result[href]"):
            href = a.get("href", "")
            if not href.startswith("/gry/"):
                continue
            full_url = f"https://www.ppe.pl{href}"
            caption = a.select_one(".result-caption div")
            name = _ws(caption.get_text(strip=True)) if caption else href.split("/")[-2].replace("-", " ")
            out.append({"name": name, "url": full_url, "snippet": ""})
            if len(out) >= max_results:
                break
        logger.info("PPE API search '%s' -> %d results", title, len(out))
        return out
    except Exception as e:
        logger.debug("PPE API search error: %s", e)
        return []


def _search(title: str) -> list[dict]:
    """Search PPE.pl native API first, fallback to DDG/Bing."""
    results = _ppe_api_search(title)
    if results:
        return results
    # Fallback to search engines (may fail due to CAPTCHA/JS requirements)
    results = _bing_search(title)
    if not results:
        results = _ddg_search(title)
    return results


def _best_match(items: list[dict], title: str) -> dict | None:
    if not items:
        return None
    ct = _canon(title)
    words = set(w for w in ct.split() if len(w) > 2)
    # Exact match
    for item in items:
        if _canon(item["name"]) == ct:
            return item
    # All significant words present
    for item in items:
        iw = set(_canon(item["name"]).split())
        if words and words.issubset(iw):
            return item
    # Fuzzy >= threshold
    best, score = None, 0.0
    for item in items:
        s = _sim(title, item["name"])
        if s > score:
            score, best = s, item
    return best if score >= MIN_MATCH else None


# -- Page parsing --

def _extract_title(soup) -> str:
    h1 = soup.find("h1")
    return _ws(h1.get_text(" ", strip=True)) if h1 else ""


def _extract_desc(soup) -> str:
    content = soup.select_one("div.content.game")
    if not content:
        return ""
    for onnet in content.select("div.onnetwork"):
        onnet.decompose()
    parts = []
    for p in content.find_all("p"):
        t = _ws(p.get_text(" ", strip=True).replace("\xa0", " "))
        if not t or t.lower().startswith("dalsza"):
            continue
        parts.append(t)
    return "\n\n".join(parts)


def _extract_rating(lines: list[str]) -> float | None:
    for i, ln in enumerate(lines):
        if re.search(r"\bocen(?:y)?\b", ln, re.IGNORECASE):
            for k in range(i - 1, max(-1, i - 8), -1):
                if re.fullmatch(r"\d{1,2}[.,]\d", lines[k]):
                    try:
                        return float(lines[k].replace(",", "."))
                    except ValueError:
                        pass
            m = re.search(r"(\d{1,2}[.,]\d)", ln)
            if m:
                try:
                    return float(m.group(1).replace(",", "."))
                except ValueError:
                    pass
            break
    return None


def _find_after(lines: list[str], label: str) -> str | None:
    for i, ln in enumerate(lines):
        if ln == label:
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j]:
                    return lines[j]
    return None


def _extract_date(lines: list[str]) -> str | None:
    for i, ln in enumerate(lines):
        if ln == "Swiat:" or ln == "\u015awiat:":
            if any(x == "Premiery" for x in lines[max(0, i - 6):i + 1]):
                for j in range(i + 1, min(i + 6, len(lines))):
                    if _DATE_RE.match(lines[j]):
                        parts = lines[j].split(".")
                        if len(parts) == 3:
                            return f"{parts[2]}-{parts[1]}-{parts[0]}"
                        return lines[j]
    return None


def _extract_screenshots(soup) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    # Method 1: parse data-elements JSON from gallery widget (most reliable)
    import json as _json
    for div in soup.find_all(attrs={"data-elements": True}):
        try:
            elements = _json.loads(div["data-elements"])
            for el in elements:
                src = el.get("src", "")
                if src and src not in seen and not src.startswith("data:"):
                    seen.add(src)
                    out.append(src)
        except Exception:
            pass

    # Method 2: find data-src and data-srcset attributes (lazy-loaded images)
    if not out:
        for img in soup.find_all("img"):
            for attr in ("data-src", "data-original", "src"):
                val = (img.get(attr) or "").strip()
                if val and not val.startswith("data:") and "pliki.ppe.pl" in val:
                    if val not in seen:
                        seen.add(val)
                        out.append(val)
                    break

    # Filter out non-screenshot images (avatars, icons, ads)
    bad = ("avatar", "emote", "icon", "logo", "flag", "banner", "sprite", "done", "close", "cropper")
    out = [u for u in out if not any(b in u.lower() for b in bad)]
    return out


def _img_url(tag) -> str:
    for attr in ("data-src", "data-original", "data-lazy-src", "src"):
        val = (tag.get(attr) or "").strip()
        if val and not val.startswith("data:"):
            return urljoin("https://www.ppe.pl", val)
    srcset = (tag.get("srcset") or "").strip()
    if srcset:
        return urljoin("https://www.ppe.pl", srcset.split(",")[0].strip().split(" ")[0])
    return ""


def _extract_developer(soup) -> str | None:
    try:
        for row in soup.select(".game-details .row"):
            lbl = row.select_one(".row-label")
            if lbl and "Producent" in lbl.get_text():
                dev = row.get_text(strip=True).replace(lbl.get_text(strip=True), "").strip()
                return dev if dev else None
    except Exception:
        pass
    return None


def _scrape_page(url: str) -> dict[str, Any]:
    try:
        r = _get(url)
        if r.status_code != 200:
            return {}
        soup = BeautifulSoup(r.text, "html.parser")
        lines = _lines(soup)
        data: dict[str, Any] = {"source_url": url}
        title = _extract_title(soup)
        if title:
            data["title"] = title
        desc = _extract_desc(soup)
        if desc:
            data["description"] = desc
        rating = _extract_rating(lines)
        if rating is not None:
            data["rating"] = rating
        genre = _find_after(lines, "Gatunek:")
        if genre:
            data["genre"] = genre
        date = _extract_date(lines)
        if date:
            data["release_date"] = date
        dev = _extract_developer(soup)
        if dev:
            data["developer"] = dev
        shots = _extract_screenshots(soup)
        if shots:
            data["screenshots"] = shots
        return data
    except Exception as e:
        logger.debug("PPE scrape error for %s: %s", url, e)
        return {}


# -- Plugin class --

class Plugin:
    """PPE.pl metadata provider - implements MetadataProviderSpec hooks."""

    @hookimpl
    def metadata_provider_name(self) -> str:
        return "PPE.pl"

    @hookimpl
    def metadata_provider_id(self) -> str:
        return "ppe"

    @hookimpl
    def metadata_search_game(self, query: str) -> list[dict[str, Any]]:
        results = _search(query)
        out = []
        for item in results:
            if item.get("_captcha"):
                continue
            out.append({
                "provider_id": "ppe",
                "provider_game_id": item["url"],
                "name": item["name"],
                "snippet": item.get("snippet", ""),
            })
        return out

    @hookimpl
    def metadata_get_game(self, provider_game_id: str) -> dict[str, Any] | None:
        if not provider_game_id.startswith("http"):
            return None
        data = _scrape_page(provider_game_id)
        if not data:
            return None
        return {
            "provider_id": "ppe",
            "provider_game_id": provider_game_id,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "rating": data.get("rating"),
            "genre": data.get("genre", ""),
            "release_date": data.get("release_date", ""),
            "developer": data.get("developer", ""),
            "screenshots": data.get("screenshots", []),
            "source_url": data.get("source_url", provider_game_id),
        }

    @hookimpl
    def metadata_get_cover_url(self, provider_game_id: str) -> str | None:
        if not provider_game_id.startswith("http"):
            return None
        data = _scrape_page(provider_game_id)
        shots = data.get("screenshots", [])
        return shots[0] if shots else None
