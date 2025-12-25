# ==================================================
# daily/holidays/holidays_daily.py — Daily Holidays Sender
# ==================================================
#
# Posts today's holidays (static + dynamic) to configured Discord channels.
#
# Layer: Daily
# ==================================================

import logging
from datetime import datetime, timedelta, timezone, time, date
from typing import Optional

import discord
from discord.ext import tasks

from services.channel_ids import parse_chat_ids
from services.holidays_service import get_today_holidays
from services.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

logger = logging.getLogger("holidays_daily")

TZ = timezone(timedelta(hours=3))  # GMT+3 timezone

# Accept one or many channel IDs, comma-separated.
HOLIDAYS_CHANNEL_IDS = parse_chat_ids("HOLIDAYS_CHANNEL_IDS")

_last_sent: Optional[date] = None


def build_flag(h) -> str:
    """Return first country flag emoji for a holiday entry."""
    countries = h.get("countries") or []
    if not countries:
        return "🌍"
    country = countries[0]
    return COUNTRY_FLAGS.get(country, "🌍")


def build_category_line(h) -> str:
    """Return first category with emoji (formatted for embed)."""
    categories = h.get("categories") or []
    if not categories:
        return ""

    main = categories[0]
    emoji = CATEGORY_EMOJIS.get(main, "")
    return f"{emoji} `{main}`" if emoji else f"`{main}`"


async def _send_embed_to_channels(bot: discord.Client, embed: discord.Embed) -> None:
    if not HOLIDAYS_CHANNEL_IDS:
        return

    for channel_id in HOLIDAYS_CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if not channel:
            logger.warning("Channel %s not found.", channel_id)
            continue
        try:
            await channel.send(embed=embed)
        except Exception:
            logger.exception("Failed to send holidays embed to channel %s.", channel_id)


def _build_today_embed(today: date) -> Optional[discord.Embed]:
    todays = get_today_holidays(today=today)
    if not todays:
        return None

    embed = discord.Embed(
        title="🎉 Today's Holidays",
    )

    for h in todays:
        embed.add_field(
            name=f"{build_flag(h)} {h.get('name', 'Holiday')}",
            value=build_category_line(h) or " ",
            inline=False,
        )
    return embed


@tasks.loop(time=time(hour=10, minute=1, tzinfo=TZ))
async def send_holidays_daily():
    """Scheduled daily job (10:01 GMT+3)."""
    global _last_sent

    bot = send_holidays_daily.bot
    now = datetime.now(TZ)
    today = now.date()

    if _last_sent == today:
        return

    embed = _build_today_embed(today)
    if not embed:
        logger.info("No holidays today.")
        return

    await _send_embed_to_channels(bot, embed)
    _last_sent = today
    logger.info("Holidays sent for %s.", today.isoformat())


# ==================================================
# One-Time Recovery (Bot Restart After 10:01)
# ==================================================
async def send_once_if_missed_holidays():
    global _last_sent

    bot = send_once_if_missed_holidays.bot
    now = datetime.now(TZ)
    scheduled = now.replace(hour=10, minute=1, second=0, microsecond=0)

    if now <= scheduled:
        return

    today = now.date()
    if _last_sent == today:
        return

    embed = _build_today_embed(today)
    if not embed:
        return

    logger.info("Bot restarted after schedule → sending missed holidays.")
    await _send_embed_to_channels(bot, embed)
    _last_sent = today
