# ==================================================
# daily/banlu/banlu_daily.py — Naughty Dog Daily Quote
# ==================================================
#
# Posts a random quote + random official Steam screenshot
# for The Last of Us™ Part I.
#
# bot.py imports:
#   from daily.banlu.banlu_daily import (send_banlu_daily, send_banlu_once)
#
# bot.py injects:
#   send_banlu_daily.bot = bot
#   send_banlu_once.bot = bot
# ==================================================

import json
import logging
import os
import random
import time as time_module
import urllib.request
from datetime import datetime, timezone, time, date
from zoneinfo import ZoneInfo
from typing import Optional

import discord
from discord.ext import tasks

from services.channel_ids import parse_chat_ids_from_env

logger = logging.getLogger("banlu_daily")

# --- TZ: same pattern as holidays/birthday ---
TZ_NAME = os.getenv("BOT_TZ", "Europe/Moscow")
try:
    TZ = ZoneInfo(TZ_NAME)
except Exception:
    logger.warning("Invalid BOT_TZ=%s, fallback to UTC", TZ_NAME)
    TZ = timezone.utc

# --- Channels (same pattern) ---
BANLU_CHANNEL_ID = parse_chat_ids_from_env("BANLU_CHANNEL_ID")
if not BANLU_CHANNEL_ID:
    # backwards compat if you ever used this old name
    BANLU_CHANNEL_ID = parse_chat_ids_from_env("BANLU_CHANNEL_IDS")

# --- Steam source ---
STEAM_APP_ID = int(os.getenv("BANLU_STEAM_APP_ID", "1888930"))
STEAM_STORE_URL = os.getenv(
    "BANLU_STEAM_URL",
    f"https://store.steampowered.com/app/{STEAM_APP_ID}/The_Last_of_Us_Part_I/",
)
STEAM_APPDETAILS_URL = f"https://store.steampowered.com/api/appdetails?appids={STEAM_APP_ID}&l=english"

# cache
_STEAM_MEDIA_CACHE: list[str] = []
_STEAM_MEDIA_CACHE_TS: float = 0.0

# --- Content ---
BANLU_QUOTES = [
    "The world doesn’t need heroes. It needs survivors.",
    "You can’t outrun what you are.",
    "Sometimes the only way out is through.",
    "Every choice costs something.",
    "Hope is dangerous. But so is giving up.",
]

DEFAULT_COLOR = 0x2F3136
_last_sent: Optional[date] = None


def _fetch_steam_media_urls() -> list[str]:
    """
    Official Steam source via appdetails API.
    Returns a list of image URLs (screenshots + fallback images).
    """
    req = urllib.request.Request(
        STEAM_APPDETAILS_URL,
        headers={"User-Agent": "Mozilla/5.0 (Just_Quotes/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        logger.warning("Steam appdetails fetch failed: %s", e)
        return []

    try:
        block = payload.get(str(STEAM_APP_ID), {})
        if not block.get("success"):
            return []
        data = block.get("data", {}) or {}
    except Exception:
        return []

    urls: list[str] = []

    # screenshots
    for s in (data.get("screenshots") or []):
        full = s.get("path_full")
        if full:
            urls.append(full)

    # nice fallbacks (still official)
    for key in ("background_raw", "header_image"):
        v = data.get(key)
        if isinstance(v, str) and v:
            urls.append(v)

    # de-dup keep order
    seen = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)

    return out[:80]


def _get_cached_media(ttl_seconds: int = 6 * 60 * 60) -> list[str]:
    global _STEAM_MEDIA_CACHE, _STEAM_MEDIA_CACHE_TS

    now = time_module.time()
    if _STEAM_MEDIA_CACHE and (now - _STEAM_MEDIA_CACHE_TS) < ttl_seconds:
        return _STEAM_MEDIA_CACHE

    media = _fetch_steam_media_urls()
    if media:
        _STEAM_MEDIA_CACHE = media
        _STEAM_MEDIA_CACHE_TS = now
    return _STEAM_MEDIA_CACHE


def _pick_media_url() -> Optional[str]:
    media = _get_cached_media()
    if not media:
        return None
    return random.choice(media)


def _build_embed() -> discord.Embed:
    quote = random.choice(BANLU_QUOTES)

    embed = discord.Embed(
        title="🐶 Naughty Dog says…",
        description=quote,
        color=DEFAULT_COLOR,
        url=STEAM_STORE_URL,
        timestamp=datetime.now(timezone.utc),
    )

    img = _pick_media_url()
    if img:
        embed.set_image(url=img)

    footer = os.getenv("BANLU_FOOTER", "Daily quote")
    embed.set_footer(text=footer)
    return embed


async def _send_to_channels(bot: discord.Client, *, embed: discord.Embed) -> None:
    if not BANLU_CHANNEL_ID:
        logger.info("No BANLU_CHANNEL_ID configured, skipping Ban'Lu/NaughtyDog send.")
        return

    for channel_id in BANLU_CHANNEL_ID:
        channel = bot.get_channel(channel_id)
        if channel is None:
            logger.warning("Channel %s not found.", channel_id)
            continue
        try:
            await channel.send(embed=embed)
        except Exception:
            logger.exception("Failed to send embed to channel %s.", channel_id)


@tasks.loop(time=time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily() -> None:
    """Scheduled daily job (10:00 in BOT_TZ)."""
    global _last_sent
    bot = send_banlu_daily.bot  # type: ignore[attr-defined]

    today = datetime.now(TZ).date()
    if _last_sent == today:
        return

    await _send_to_channels(bot, embed=_build_embed())
    _last_sent = today
    logger.info("Naughty Dog quote sent for %s.", today.isoformat())


async def send_banlu_once() -> None:
    """
    One-time recovery on startup:
    if bot starts AFTER 10:00 and today's quote wasn't sent yet — send once.
    """
    global _last_sent
    bot = send_banlu_once.bot  # type: ignore[attr-defined]

    now = datetime.now(TZ)
    scheduled = now.replace(hour=10, minute=0, second=0, microsecond=0)
    if now <= scheduled:
        return

    today = now.date()
    if _last_sent == today:
        return

    logger.info("Bot restarted after schedule → sending missed Naughty Dog quote.")
    await _send_to_channels(bot, embed=_build_embed())
    _last_sent = today
