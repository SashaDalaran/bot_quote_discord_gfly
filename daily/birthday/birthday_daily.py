# ==================================================
# daily/birthday/birthday_daily.py — Daily Guild Events Sender
# ==================================================
#
# Posts guild events (Challenges / Heroes / Birthdays) to configured Discord channels.
#
# Layer: Daily
#
# Responsibilities:
# - Schedule recurring jobs via discord.ext.tasks
# - Load/normalize/format content via services/
# - Send messages to configured channels
#
# Boundaries:
# - Daily jobs are orchestration only: no domain logic here.
#
# ==================================================

import logging
import os
from datetime import datetime, timedelta, timezone, time, date
from zoneinfo import ZoneInfo
from typing import Optional

import discord
from discord.ext import tasks

from services.channel_ids import parse_chat_ids_from_env
from services.birthday_service import load_birthday_events, get_today_birthday_payload
from services.birthday_format import build_guild_events_embed

logger = logging.getLogger("birthday_daily")

TZ_NAME = os.getenv("BOT_TZ", "Europe/Moscow")
try:
    TZ = ZoneInfo(TZ_NAME)
except Exception:
    logger.warning("Invalid BOT_TZ=%s, fallback to UTC", TZ_NAME)
    TZ = timezone.utc

# Accept one or many channel IDs, comma-separated.
BIRTHDAY_CHANNEL_ID = parse_chat_ids_from_env("BIRTHDAY_CHANNEL_ID")

# In-memory guard to avoid double-sends after restarts.
_last_sent: Optional[date] = None


async def _send_to_channels(bot: discord.Client, *, embed: discord.Embed) -> None:
    """Send an embed to all configured channels."""
    if not BIRTHDAY_CHANNEL_ID:
        return

    for channel_id in BIRTHDAY_CHANNEL_ID:
        channel = bot.get_channel(channel_id)
        if channel is None:
            logger.warning("Channel %s not found.", channel_id)
            continue

        try:
            await channel.send(embed=embed)
        except Exception:
            logger.exception("Failed to send guild events message to channel %s.", channel_id)


def _build_today_embed(today: date) -> Optional[discord.Embed]:
    events = load_birthday_events()
    payload = get_today_birthday_payload(events=events, today=today)
    if not payload:
        return None
    return build_guild_events_embed(payload=payload, today=today)


@tasks.loop(time=time(hour=10, minute=2, tzinfo=TZ))
async def send_birthday_daily():
    """Scheduled daily job (10:05 GMT+3)."""
    global _last_sent

    bot = send_birthday_daily.bot
    now = datetime.now(TZ)
    today = now.date()

    if _last_sent == today:
        return

    embed = _build_today_embed(today)
    if not embed:
        return

    await _send_to_channels(bot, embed=embed)
    _last_sent = today
    logger.info("Guild events sent for %s.", today.isoformat())


# ==================================================
# One-Time Recovery (Bot Restart After 10:05)
# ==================================================
async def send_once_if_missed_birthday():
    """If the bot starts after today's scheduled time, send once."""
    global _last_sent

    bot = send_once_if_missed_birthday.bot
    now = datetime.now(TZ)
    scheduled = now.replace(hour=10, minute=5, second=0, microsecond=0)

    if now <= scheduled:
        return

    today = now.date()
    if _last_sent == today:
        return

    embed = _build_today_embed(today)
    if not embed:
        return

    logger.info("Bot restarted after schedule → sending missed guild events.")
    await _send_to_channels(bot, embed=embed)
    _last_sent = today
