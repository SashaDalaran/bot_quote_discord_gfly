# ==================================================
# daily/banlu/banlu_daily.py — Ban'Lu Daily Job
# ==================================================
#
# Posts a random Ban'Lu quote to configured Discord channels.
#
# This module is imported by bot.py like:
#   from daily.banlu.banlu_daily import (send_banlu_daily, send_banlu_once)
#
# bot.py then injects:
#   send_banlu_daily.bot = bot
#   send_banlu_once.bot = bot
#
# ==================================================

import logging
import os
import random
import datetime as dt
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional

import discord
from discord.ext import tasks

logger = logging.getLogger(__name__)

TZ = ZoneInfo(os.getenv("TZ", "Europe/Moscow"))

BANLU_QUOTES = [
    "The world doesn’t need heroes. It needs survivors.",
    "You can’t outrun what you are.",
    "Sometimes the only way out is through.",
    "Every choice costs something.",
    "Hope is dangerous. But so is giving up.",
]

DEFAULT_COLOR = 0x2F3136

_last_sent: Optional[dt.date] = None


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


def _get_channel_ids() -> list[int]:
    raw = os.getenv("BANLU_CHANNEL_IDS", "").strip()
    if not raw:
        return []
    return _parse_channel_ids(raw)


def _build_embed() -> discord.Embed:
    quote = random.choice(BANLU_QUOTES)

    embed = discord.Embed(
        title="📜 Ban'Lu says…",
        description=quote,
        color=DEFAULT_COLOR,
        timestamp=datetime.now(timezone.utc),
    )
    footer = os.getenv("BANLU_FOOTER", "Daily quote")
    embed.set_footer(text=footer)
    return embed


async def _send_to_channels(bot: discord.Client, *, embed: discord.Embed) -> None:
    channel_ids = _get_channel_ids()
    if not channel_ids:
        logger.info("No BANLU_CHANNEL_IDS configured, skipping Ban'Lu send.")
        return

    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        if channel is None:
            logger.warning("Channel %s not found.", channel_id)
            continue
        try:
            await channel.send(embed=embed)
        except Exception:
            logger.exception("Failed to send Ban'Lu message to channel %s.", channel_id)


# ✅ FIX: используем dt.time(...) чтобы не ловить 'module' object is not callable
@tasks.loop(time=dt.time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily() -> None:
    bot = send_banlu_daily.bot  # type: ignore[attr-defined]
    embed = _build_embed()
    await _send_to_channels(bot, embed=embed)

    global _last_sent
    _last_sent = dt.datetime.now(TZ).date()


async def send_banlu_once() -> None:
    """
    Fallback on startup:
    If the bot restarted AFTER the scheduled time (10:00 in TZ),
    and we haven't sent today yet — send once.
    """
    global _last_sent

    bot = send_banlu_once.bot  # type: ignore[attr-defined]

    now = dt.datetime.now(TZ)
    scheduled = now.replace(hour=10, minute=0, second=0, microsecond=0)

    # If it's not yet time — do nothing
    if now <= scheduled:
        return

    today = now.date()
    if _last_sent == today:
        return

    embed = _build_embed()

    logger.info("Bot restarted after schedule → sending missed Ban'Lu quote.")
    await _send_to_channels(bot, embed=embed)

    _last_sent = today
