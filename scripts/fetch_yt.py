#!/usr/bin/env python3
"""Fetch a YouTube transcript and write it to a markdown file.

Usage: fetch_yt.py <url> <output_path>
Exits non-zero with a readable message on failure.
"""
import re
import sys
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

try:
    import urllib.request
except ImportError:
    urllib = None


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|/shorts/|youtu\.be/|/embed/|/v/)([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    raise ValueError(f"Could not extract video ID from: {url}")


def fetch_title(video_id: str) -> str:
    try:
        import json
        req = urllib.request.Request(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data.get("title", video_id)
    except Exception:
        return video_id


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: fetch_yt.py <url> <output_path>", file=sys.stderr)
        return 2

    url, out_path = sys.argv[1], Path(sys.argv[2])

    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
        segments = fetched.to_raw_data()
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for {video_id}", file=sys.stderr)
        return 1
    except NoTranscriptFound:
        print(f"No transcript found for {video_id}", file=sys.stderr)
        return 1
    except VideoUnavailable:
        print(f"Video unavailable: {video_id}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Transcript fetch failed: {e}", file=sys.stderr)
        return 1

    title = fetch_title(video_id)
    body = " ".join(s["text"].replace("\n", " ").strip() for s in segments if s.get("text"))
    body = re.sub(r"\s+", " ", body).strip()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(f"# {title}\n\n*YouTube transcript — video ID `{video_id}`.*\n\n{body}\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
