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
from datetime import datetime, timedelta, timezone, time, date
from zoneinfo import ZoneInfo
from typing import Optional

import discord
from discord.ext import tasks

from services.channel_ids import parse_chat_ids_from_env
from services.banlu_service import load_banlu_quotes, get_random_banlu_quote, format_banlu_message

import random
import re
import time
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
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=7) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    urls = set(
        re.findall(
            r"https://shared\.fastly\.steamstatic\.com/store_item_assets/steam/apps/1888930/[^\"\s]+?\.jpg[^\"\s]*",
            html,
        )
    )
    shots = [u for u in urls if "/ss_" in u]
    shots_1080 = [u for u in shots if "1920x1080" in u]
    if shots_1080:
        return sorted(shots_1080)
    if shots:
        return sorted(shots)
    return []

def _choose_banlu_image_url() -> str:
    """Pick a random image for the Ban'Lu embed (cached)."""
    global _STEAM_SCREENSHOT_CACHE_TS, _STEAM_SCREENSHOT_CACHE
    now = time.time()

    # Refresh cache every 12 hours
    if (now - _STEAM_SCREENSHOT_CACHE_TS) > 12 * 3600 or not _STEAM_SCREENSHOT_CACHE:
        try:
            _STEAM_SCREENSHOT_CACHE = _fetch_steam_screenshots()
            _STEAM_SCREENSHOT_CACHE_TS = now
        except Exception as e:
            logger.warning("Steam image fetch failed: %s", e)

    if _STEAM_SCREENSHOT_CACHE:
        return random.choice(_STEAM_SCREENSHOT_CACHE)

    return "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1888930/header.jpg"

logger = logging.getLogger("banlu_daily")

TZ_NAME = os.getenv("BOT_TZ", "Europe/Moscow")
try:
    TZ = ZoneInfo(TZ_NAME)
except Exception:
    logger.warning("Invalid BOT_TZ=%s, fallback to UTC", TZ_NAME)
    TZ = timezone.utc


BANLU_FILE = os.getenv("BANLU_QUOTES_FILE", "data/quotersbanlu.txt")
BANLU_CHANNELS = parse_chat_ids_from_env("BANLU_CHANNEL_ID")  # one or many, comma-separated

# Optional media/links for the quote "tile".
# Defaults are set to The Last of Us Part I Steam page.
BANLU_LINK_URL = os.getenv(
    "BANLU_LINK_URL",
    "https://store.steampowered.com/app/1888930/The_Last_of_Us_Part_I/",
)
BANLU_IMAGE_URL = os.getenv(
    "BANLU_IMAGE_URL",
    "https://cdn.akamai.steamstatic.com/steam/apps/1888930/header.jpg",
)

# Preload quotes once at startup
_banlu_quotes = load_banlu_quotes(BANLU_FILE)

_last_sent: Optional[date] = None


async def _send_to_channels(bot: discord.Client, *, embed: discord.Embed) -> None:
    if not BANLU_CHANNELS:
        return

    for channel_id in BANLU_CHANNELS:
        channel = bot.get_channel(channel_id)
        if channel is None:
            logger.warning("Channel %s not found.", channel_id)
            continue
        try:
            await channel.send(embed=embed)
        except Exception:
            logger.exception("Failed to send Ban'Lu message to channel %s.", channel_id)


def _build_embed() -> Optional[discord.Embed]:
    quote = get_random_banlu_quote(_banlu_quotes)
    if not quote:
        return None

    text = format_banlu_message(quote)
    embed = discord.Embed(
        title="💬 Ban'Lu quote",
        description=text,
        url=BANLU_LINK_URL,
    )
    # One image per embed: randomize by default (can be overridden via BANLU_IMAGE_URL or BANLU_IMAGE_URLS).
    embed.set_image(url=os.getenv("BANLU_IMAGE_URL") or _choose_banlu_image_url())
    return embed


@tasks.loop(time=time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily():
    """Scheduled daily job (10:00 GMT+3)."""
    global _last_sent

    bot = send_banlu_daily.bot
    now = datetime.now(TZ)
    today = now.date()

    if _last_sent == today:
        return

    embed = _build_embed()
    if not embed:
        return

    await _send_to_channels(bot, embed=embed)
    _last_sent = today
    logger.info("Ban'Lu quote sent for %s.", today.isoformat())


# ==================================================
# One-Time Recovery (Bot Restart After 10:00)
# ==================================================
async def send_banlu_once():
    global _last_sent

    bot = send_banlu_once.bot
    now = datetime.now(TZ)
    scheduled = now.replace(hour=10, minute=0, second=0, microsecond=0)

    if now <= scheduled:
        return

    today = now.date()
    if _last_sent == today:
        return

    embed = _build_embed()
    if not embed:
        return

    logger.info("Bot restarted after schedule → sending missed Ban'Lu quote.")
    await _send_to_channels(bot, embed=embed)
    _last_sent = today
