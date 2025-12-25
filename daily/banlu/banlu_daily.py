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
from datetime import datetime, timedelta, timezone, time, date
from typing import Optional

import discord
from discord.ext import tasks

from services.channel_ids import parse_chat_ids
from services.banlu_service import load_banlu_quotes, get_random_banlu_quote, format_banlu_message

logger = logging.getLogger("banlu_daily")

TZ = timezone(timedelta(hours=3))  # GMT+3

BANLU_FILE = os.getenv("BANLU_QUOTES_FILE", "data/quotersbanlu.txt")
BANLU_CHANNEL_IDS = parse_chat_ids("BANLU_CHANNEL_ID")  # accepts one or many (comma-separated)

# Preload quotes once at startup
_banlu_quotes = load_banlu_quotes(BANLU_FILE)

_last_sent: Optional[date] = None


async def _send_to_channels(bot: discord.Client, text: str) -> None:
    if not BANLU_CHANNEL_IDS:
        return

    for channel_id in BANLU_CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel is None:
            logger.warning("Channel %s not found.", channel_id)
            continue
        try:
            await channel.send(text)
        except Exception:
            logger.exception("Failed to send Ban'Lu message to channel %s.", channel_id)


def _build_message() -> Optional[str]:
    quote = get_random_banlu_quote(_banlu_quotes)
    if not quote:
        return None
    return format_banlu_message(quote)


@tasks.loop(time=time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily():
    """Scheduled daily job (10:00 GMT+3)."""
    global _last_sent

    bot = send_banlu_daily.bot
    now = datetime.now(TZ)
    today = now.date()

    if _last_sent == today:
        return

    text = _build_message()
    if not text:
        return

    await _send_to_channels(bot, text)
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

    text = _build_message()
    if not text:
        return

    logger.info("Bot restarted after schedule → sending missed Ban'Lu quote.")
    await _send_to_channels(bot, text)
    _last_sent = today
