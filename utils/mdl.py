import urllib.request
import urllib.parse
import json
import re


def _fetch(url: str, accept: str = "text/html") -> str:
    """Simple HTTP GET using only stdlib — no aiohttp needed."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": accept,
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.read().decode("utf-8")


def search_drama(query: str) -> dict | None:
    """
    Search MyDramaList for a drama and return structured data.
    Uses the MDL search API for reliable poster images, then
    scrapes the detail page for full info.
    """
    try:
        encoded = urllib.parse.quote(query)

        # Step 1: use MDL's internal search API to get slug + poster
        api_url = f"https://mydramalist.com/api/v1/search/titles?q={encoded}&limit=1"
        poster = None
        slug = None

        try:
            raw = _fetch(api_url, accept="application/json")
            data = json.loads(raw)
            items = data.get("data", {}).get("list", []) or data.get("list", [])
            if items:
                item = items[0]
                slug = item.get("slug") or item.get("permalink")
                # Poster comes back as a relative or absolute URL
                img = item.get("cover") or item.get("image") or item.get("poster") or ""
                if img:
                    poster = img if img.startswith("http") else f"https://mydramalist.com{img}"
        except Exception:
            pass  # fall through to HTML scrape for slug

        # Step 2: if API didn't give us a slug, scrape the search results page
        if not slug:
            search_url = f"https://mydramalist.com/search?q={encoded}&adv=titles"
            html = _fetch(search_url)
            slug_match = re.search(
                r'<h6[^>]*class="[^"]*title[^"]*"[^>]*>\s*<a href="(/\d+-[^"]+)"', html
            )
            if not slug_match:
                slug_match = re.search(r'href="(/\d{4,}-[a-z0-9-]+)"', html)
            if not slug_match:
                return None
            slug = slug_match.group(1)

        drama_url = f"https://mydramalist.com{slug}" if not slug.startswith("http") else slug
        return _get_drama_details(drama_url, poster_override=poster)

    except Exception as e:
        print(f"[MDL] Search error: {e}")
        return None


def _get_drama_details(url: str, poster_override: str | None = None) -> dict | None:
    """Scrape drama details page and return structured dict."""
    try:
        html = _fetch(url)

        # Title
        title_match = re.search(
            r'<h1[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</h1>', html
        )
        title = title_match.group(1).strip() if title_match else "Unknown"

        # Rating
        rating_match = re.search(
            r'<span[^>]*class="[^"]*score[^"]*"[^>]*>\s*([\d.]+)\s*</span>', html
        )
        if not rating_match:
            rating_match = re.search(r'"ratingValue"\s*:\s*"([\d.]+)"', html)
        rating = rating_match.group(1) if rating_match else "N/A"

        # Episodes
        ep_match = re.search(
            r'Episodes.*?<span[^>]*>\s*(\d+)\s*</span>', html, re.DOTALL
        )
        if not ep_match:
            ep_match = re.search(r'"numberOfEpisodes"\s*:\s*"?(\d+)"?', html)
        episodes = ep_match.group(1) if ep_match else "N/A"

        # Year / aired — only match realistic drama years (1900–2099)
        year_match = re.search(
            r'(?:aired|Date Aired|Release)[^<]{0,200}?((?:19|20)\d{2})',
            html, re.IGNORECASE | re.DOTALL
        )
        if not year_match:
            year_match = re.search(r'"startDate"\s*:\s*"((?:19|20)\d{2})', html)
        if not year_match:
            year_match = re.search(r'\b((?:19|20)\d{2})\b', html)
        year = year_match.group(1) if year_match else "N/A"

        # Genres — grab up to 4
        genres = re.findall(
            r'href="/search\?[^"]*genres[^"]*"[^>]*>([^<]+)</a>', html
        )
        genres = list(dict.fromkeys(genres))[:4]

        # Country
        country_match = re.search(
            r'Country.*?<a[^>]+>([^<]+)</a>', html, re.DOTALL
        )
        country = country_match.group(1).strip() if country_match else "N/A"

        # Synopsis
        synopsis_match = re.search(
            r'<div[^>]*class="[^"]*show-synopsis[^"]*"[^>]*>.*?<p[^>]*>(.*?)</p>',
            html, re.DOTALL
        )
        if not synopsis_match:
            synopsis_match = re.search(r'"description"\s*:\s*"([^"]{20,})"', html)
        if synopsis_match:
            raw = synopsis_match.group(1)
            synopsis = re.sub(r'<[^>]+>', '', raw).strip()
            synopsis = re.sub(r'\s+', ' ', synopsis)
            if len(synopsis) > 300:
                synopsis = synopsis[:300] + "..."
        else:
            synopsis = "No synopsis available."

        # Poster — prefer API result, fall back to og:image meta tag (most reliable)
        poster = poster_override
        if not poster:
            og_match = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', html)
            if not og_match:
                og_match = re.search(r'<meta[^>]*content="([^"]+)"[^>]*property="og:image"', html)
            poster = og_match.group(1) if og_match else None

        return {
            "title": title,
            "url": url,
            "rating": rating,
            "episodes": episodes,
            "year": year,
            "genres": genres,
            "country": country,
            "synopsis": synopsis,
            "poster": poster,
        }

    except Exception as e:
        print(f"[MDL] Detail scrape error: {e}")
        return None