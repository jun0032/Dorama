import urllib.request
import urllib.parse
import json
import base64
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

_token_cache = {"token": None, "expires_at": 0}


def _get_access_token() -> str | None:
    """Get a Spotify access token using Client Credentials flow."""
    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("[Spotify] Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in .env")
        return None

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            _token_cache["token"] = result["access_token"]
            _token_cache["expires_at"] = time.time() + result["expires_in"]
            return _token_cache["token"]
    except Exception as e:
        print(f"[Spotify] Token error: {e}")
        return None


def _spotify_get(endpoint: str, params: dict) -> dict | None:
    """Make an authenticated GET request to the Spotify API."""
    token = _get_access_token()
    if not token:
        return None

    query = urllib.parse.urlencode(params)
    url = f"https://api.spotify.com/v1/{endpoint}?{query}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"[Spotify] API error: {e}")
        return None


def _is_full_album(name: str) -> bool:
    """Return True if the album looks like a full OST, not a single part."""
    part_pattern = re.compile(
        r'\b(part|pt\.?|vol\.?)\s*\d+\b'  # "Part 1", "Pt.2", "Vol 3"
        r'|\bsingle\b'                      # "- Single"
        r'|\bspecial\s+ost\b',              # "Special OST"
        re.IGNORECASE
    )
    return not part_pattern.search(name)


def _score_album(album: dict, drama_name: str) -> int:
    """Score an album — higher is better. Full albums ranked over parts."""
    name_lower = album["name"].lower()
    drama_lower = drama_name.lower()
    score = 0

    if _is_full_album(album["name"]):
        score += 100

    # More tracks = more likely to be full album
    score += min(album.get("total_tracks", 0), 30)

    if drama_lower in name_lower:
        score += 20
    elif _words_overlap(drama_lower, name_lower):
        score += 10

    if "ost" in name_lower or "soundtrack" in name_lower:
        score += 15

    return score


def _words_overlap(a: str, b: str) -> bool:
    """Check if two strings share significant words (3+ chars)."""
    words_a = set(w for w in a.split() if len(w) >= 3)
    words_b = set(w for w in b.split() if len(w) >= 3)
    return bool(words_a & words_b)


def search_ost(drama_name: str) -> dict | None:
    """
    Search Spotify for a K-Drama OST.
    Prioritizes full OST albums over individual parts/singles.
    """
    queries = [
        f"{drama_name} OST",
        f"{drama_name} Original Soundtrack",
        f"{drama_name} 드라마 OST",
    ]

    all_albums = []
    seen_ids = set()

    for query in queries:
        data = _spotify_get("search", {
            "q": query,
            "type": "album",
            "limit": 10,
            "market": "KR"
        })

        if not data:
            continue

        for album in data.get("albums", {}).get("items", []):
            if not album or album["id"] in seen_ids:
                continue
            name_lower = album["name"].lower()
            drama_lower = drama_name.lower()
            # Hard exclude parts/singles — don't even add them to candidates
            if not _is_full_album(album["name"]):
                continue
            # Only include albums related to this drama
            if drama_lower in name_lower or _words_overlap(drama_lower, name_lower):
                all_albums.append(album)
                seen_ids.add(album["id"])

    # Sort — full albums with more tracks first
    all_albums.sort(key=lambda a: _score_album(a, drama_name), reverse=True)

    if all_albums:
        return _format_album(all_albums[0])

    # Fallback: search playlists — better than showing a single part
    for query in [f"{drama_name} OST", f"{drama_name} full soundtrack"]:
        data = _spotify_get("search", {
            "q": query,
            "type": "playlist",
            "limit": 5,
            "market": "KR"
        })
        if data:
            for playlist in data.get("playlists", {}).get("items", []):
                if not playlist:
                    continue
                name_lower = playlist["name"].lower()
                if "ost" in name_lower or drama_name.lower() in name_lower:
                    return _format_playlist(playlist)

    return None


def _format_album(album: dict) -> dict:
    """Format a Spotify album into a clean dict."""
    tracks = []
    album_id = album["id"]
    track_data = _spotify_get(f"albums/{album_id}/tracks", {"limit": 5, "market": "KR"})
    if track_data:
        for track in track_data.get("items", [])[:5]:
            artist_names = ", ".join(a["name"] for a in track.get("artists", []))
            tracks.append({
                "name": track["name"],
                "artist": artist_names,
                "url": track.get("external_urls", {}).get("spotify", "")
            })

    images = album.get("images", [])
    poster = images[0]["url"] if images else None

    return {
        "type": "album",
        "title": album["name"],
        "url": album.get("external_urls", {}).get("spotify", ""),
        "artist": ", ".join(a["name"] for a in album.get("artists", [])),
        "release_date": album.get("release_date", "N/A")[:4],
        "total_tracks": album.get("total_tracks", 0),
        "poster": poster,
        "tracks": tracks,
    }


def _format_playlist(playlist: dict) -> dict:
    """Format a Spotify playlist into a clean dict with top 5 tracks."""
    images = playlist.get("images", [])
    poster = images[0]["url"] if images else None

    # Fetch top 5 tracks from the playlist
    tracks = []
    playlist_id = playlist["id"]
    track_data = _spotify_get(
        f"playlists/{playlist_id}/tracks",
        {"limit": 5, "market": "KR"}
    )
    if track_data:
        for item in track_data.get("items", [])[:5]:
            track = item.get("track")
            if not track:
                continue
            artist_names = ", ".join(a["name"] for a in track.get("artists", []))
            tracks.append({
                "name": track["name"],
                "artist": artist_names,
                "url": track.get("external_urls", {}).get("spotify", "")
            })

    return {
        "type": "playlist",
        "title": playlist["name"],
        "url": playlist.get("external_urls", {}).get("spotify", ""),
        "artist": playlist.get("owner", {}).get("display_name", "Various Artists"),
        "release_date": "N/A",
        "total_tracks": playlist.get("tracks", {}).get("total", 0),
        "poster": poster,
        "tracks": tracks,
    }