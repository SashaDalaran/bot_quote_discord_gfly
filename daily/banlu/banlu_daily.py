# ==================================================
# daily/banlu/banlu_daily.py — Ban'Lu Daily Job
# ==================================================
#
# Posts a random Ban'Lu quote to configured Discord channels.
#
# Layer: Daily
# ==================================================

import logging
import os
import random
import datetime as dt
from datetime import datetime, timedelta, timezone, time, date
from zoneinfo import ZoneInfo
from typing import Optional

import discord
from discord.ext import tasks

import time as time_module
import urllib.request

_STEAM_SCREENSHOT_CACHE: list[str] = []
_STEAM_SCREENSHOT_CACHE_TS: float = 0.0

def _fetch_steam_screenshots() -> list[str]:
    """Fetch screenshot URLs from the Steam store page (best-effort)."""
    url = os.getenv(
        "BANLU_STEAM_URL",
        "https://store.steampowered.com/app/1888930/The_Last_of_Us_Part_I/",
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; Just_Quotes/1.0)",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return []

    # Steam markup changes sometimes; keep this best-effort and non-fatal.
    # We search for common screenshot cdn patterns.
    candidates: list[str] = []
    for token in html.split('"'):
        if "steamstatic.com/steam/apps/" in token and ("jpg" in token or "png" in token):
            if token.startswith("http"):
                candidates.append(token)
            elif token.startswith("//"):
                candidates.append("https:" + token)

    # Deduplicate, keep order
    seen = set()
    out: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)

    return out[:50]


def _get_cached_screenshots(ttl_seconds: int = 6 * 60 * 60) -> list[str]:
    global _STEAM_SCREENSHOT_CACHE, _STEAM_SCREENSHOT_CACHE_TS

    now = time_module.time()
    if _STEAM_SCREENSHOT_CACHE and (now - _STEAM_SCREENSHOT_CACHE_TS) < ttl_seconds:
        return _STEAM_SCREENSHOT_CACHE

    shots = _fetch_steam_screenshots()
    if shots:
        _STEAM_SCREENSHOT_CACHE = shots
        _STEAM_SCREENSHOT_CACHE_TS = now
    return _STEAM_SCREENSHOT_CACHE


def _pick_screenshot() -> Optional[str]:
    shots = _get_cached_screenshots()
    if not shots:
        return None
    return random.choice(shots)


logger = logging.getLogger(__name__)

TZ = ZoneInfo(os.getenv("TZ", "Europe/Moscow"))

BANLU_QUOTES = [
    "The world doesn’t need heroes. It needs survivors.",
    "You can’t outrun what you are.",
    "Sometimes the only way out is through.",
    "Every choice costs something.",
    "Hope is dangerous. But so is giving up.",
]

DEFAULT_COLOR = 0x2F3136  # Discord dark-ish

def _parse_channel_ids(value: str) -> list[int]:
    ids: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            logger.warning("Invalid channel id: %r", part)
    return ids


def _get_target_channels(client: discord.Client) -> list[discord.abc.Messageable]:
    raw = os.getenv("BANLU_CHANNEL_IDS", "").strip()
    if not raw:
        return []

    ids = _parse_channel_ids(raw)
    out: list[discord.abc.Messageable] = []
    for cid in ids:
        ch = client.get_channel(cid)
        if ch is None:
            continue
        out.append(ch)
    return out


def _build_embed() -> discord.Embed:
    quote = random.choice(BANLU_QUOTES)
    embed = discord.Embed(
        title="📜 Ban'Lu says…",
        description=quote,
        color=DEFAULT_COLOR,
        timestamp=datetime.now(timezone.utc),
    )

    shot = _pick_screenshot()
    if shot:
        embed.set_image(url=shot)

    footer = os.getenv("BANLU_FOOTER", "Daily quote")
    embed.set_footer(text=footer)
    return embed


async def _post_to_channels(client: discord.Client) -> None:
    channels = _get_target_channels(client)
    if not channels:
        logger.info("No BANLU_CHANNEL_IDS configured, skipping.")
        return

    embed = _build_embed()
    for ch in channels:
        try:
            await ch.send(embed=embed)
        except Exception as e:
            logger.warning("Failed to send Ban'Lu daily to %s: %s", getattr(ch, "id", "?"), e)


# ✅ FIX: используем dt.time(...) вместо time(...), чтобы имя time никогда не могло стать модулем
@tasks.loop(time=dt.time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily() -> None:
    client = send_banlu_daily.client  # type: ignore[attr-defined]
    await _post_to_channels(client)


def setup_banlu_daily(client: discord.Client) -> None:
    # attach client to task (simple pattern)
    send_banlu_daily.client = client  # type: ignore[attr-defined]

    if not send_banlu_daily.is_running():
        send_banlu_daily.start()
        logger.info("Ban'Lu daily task started.")
