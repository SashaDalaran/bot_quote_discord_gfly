# ==================================================
# daily/banlu/banlu_daily.py — Ban'Lu Daily Job
# ==================================================

import logging
import os
import random
import datetime as dt
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from typing import Optional

import discord
from discord.ext import tasks

from services.channel_ids import parse_chat_ids_from_env

logger = logging.getLogger("banlu_daily")

# ✅ как в holidays/birthday: BOT_TZ
TZ_NAME = os.getenv("BOT_TZ", "Europe/Moscow")
try:
    TZ = ZoneInfo(TZ_NAME)
except Exception:
    logger.warning("Invalid BOT_TZ=%s, fallback to UTC", TZ_NAME)
    TZ = timezone.utc

# ✅ как в holidays/birthday: *_CHANNEL_ID (список, через запятую)
BANLU_CHANNEL_ID = parse_chat_ids_from_env("BANLU_CHANNEL_ID")

# совместимость: если кто-то уже настроил BANLU_CHANNEL_IDS
if not BANLU_CHANNEL_ID:
    BANLU_CHANNEL_ID = parse_chat_ids_from_env("BANLU_CHANNEL_IDS")

BANLU_QUOTES = [
    "The world doesn’t need heroes. It needs survivors.",
    "You can’t outrun what you are.",
    "Sometimes the only way out is through.",
    "Every choice costs something.",
    "Hope is dangerous. But so is giving up.",
]

DEFAULT_COLOR = 0x2F3136
_last_sent: Optional[date] = None


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
    if not BANLU_CHANNEL_ID:
        logger.info("No BANLU_CHANNEL_ID configured, skipping Ban'Lu send.")
        return

    for channel_id in BANLU_CHANNEL_ID:
        channel = bot.get_channel(channel_id)
        if channel is None:
            logger.warning("Channel %s not found.", channel_id)
            continue
        try:
            await channel.send(embed=embed)
        except Exception:
            logger.exception("Failed to send Ban'Lu message to channel %s.", channel_id)


@tasks.loop(time=dt.time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily() -> None:
    global _last_sent
    bot = send_banlu_daily.bot  # type: ignore[attr-defined]

    today = dt.datetime.now(TZ).date()
    if _last_sent == today:
        return

    await _send_to_channels(bot, embed=_build_embed())
    _last_sent = today
    logger.info("Ban'Lu sent for %s.", today.isoformat())


async def send_banlu_once() -> None:
    """Send once if bot started after schedule (10:00) and not sent today yet."""
    global _last_sent
    bot = send_banlu_once.bot  # type: ignore[attr-defined]

    now = dt.datetime.now(TZ)
    scheduled = now.replace(hour=10, minute=0, second=0, microsecond=0)

    if now <= scheduled:
        return

    today = now.date()
    if _last_sent == today:
        return

    logger.info("Bot restarted after schedule → sending missed Ban'Lu quote.")
    await _send_to_channels(bot, embed=_build_embed())
    _last_sent = today
