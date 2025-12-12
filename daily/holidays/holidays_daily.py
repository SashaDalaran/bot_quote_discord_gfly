# ==================================================
# daily/holidays/holidays_daily.py — Daily Holidays Sender
# ==================================================

import os
import logging
from datetime import datetime, timedelta, timezone, time

import discord
from discord.ext import tasks

from commands.holidays_cmd import load_all_holidays
from core.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

logger = logging.getLogger("holidays_daily")


# ===========================
# Configuration
# ===========================
TZ = timezone(timedelta(hours=3))  # GMT+3 timezone

# List of target channels (environment variable)
HOLIDAYS_CHANNEL_IDS = [
    cid.strip()
    for cid in os.getenv("HOLIDAYS_CHANNEL_IDS", "").split(",")
    if cid.strip().isdigit()
]


# ===========================
# Utility Helpers
# ===========================
def is_today(h) -> bool:
    """Return True if the holiday occurs today (local TZ)."""
    today = datetime.now(TZ).date()
    return h.get("parsed_date") == today


def build_flag(h) -> str:
    """Return emoji flag for the holiday's country."""
    country = (
        h.get("country")
        or (h.get("countries")[0] if h.get("countries") else "")
    )
    return COUNTRY_FLAGS.get(country, "🌍")


def build_category_line(h) -> str:
    """Return first category with emoji (formatted for embed)."""
    categories = h.get("categories") or []
    if not categories:
        return ""

    main = categories[0]
    emoji = CATEGORY_EMOJIS.get(main, "")
    return f"{emoji} `{main}`" if emoji else f"`{main}`"


# ==================================================
# Daily Scheduled Holidays Task — 10:01 GMT+3
# ==================================================
@tasks.loop(time=time(hour=10, minute=1, tzinfo=TZ))
async def send_holidays_daily():
    """
    Send the list of today's holidays daily at 10:01 GMT+3.
    Bot reference is injected from bot.py.
    """
    bot = send_holidays_daily.bot  # injected externally
    logger.info("Running daily holidays task...")

    holidays = load_all_holidays()
    todays = [h for h in holidays if is_today(h)]

    if not todays:
        logger.info("No holidays today.")
        return

    for channel_id in HOLIDAYS_CHANNEL_IDS:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            logger.warning(f"Channel {channel_id} not found.")
            continue

        embed = discord.Embed(
            title="🎉 Today's Holidays",
            color=0x00AEEF,
        )

        for h in todays:
            embed.add_field(
                name=f"{build_flag(h)} {h['name']}",
                value=build_category_line(h) or " ",
                inline=False,
            )

        try:
            await channel.send(embed=embed)
            logger.info(f"Sent daily holidays to {channel_id}")
        except Exception as e:
            logger.exception(
                f"Failed to send daily holidays to {channel_id}: {e}"
            )


# ==================================================
# One-Time Recovery (Bot Restart After 10:01)
# ==================================================
async def send_once_if_missed_holidays():
    """
    If the bot starts after the scheduled time (10:01),
    send today's holidays once on startup.
    """
    bot = send_once_if_missed_holidays.bot  # injected externally

    now = datetime.now(TZ)
    scheduled_time = now.replace(hour=10, minute=1, second=0, microsecond=0)

    # If it's not past 10:01 yet → do nothing
    if now <= scheduled_time:
        return

    holidays = load_all_holidays()
    todays = [h for h in holidays if is_today(h)]

    if not todays:
        logger.info("No holidays today (missed-task check).")
        return

    logger.info("Bot restarted after 10:01 → sending holiday list once...")

    for channel_id in HOLIDAYS_CHANNEL_IDS:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            logger.warning(f"Channel {channel_id} not found.")
            continue

        embed = discord.Embed(
            title="🎉 Today's Holidays",
            color=0x00AEEF,
        )

        for h in todays:
            embed.add_field(
                name=f"{build_flag(h)} {h['name']}",
                value=build_category_line(h) or " ",
                inline=False,
            )

        try:
            await channel.send(embed=embed)
            logger.info(f"Sent missed holidays to {channel_id}")
        except Exception as e:
            logger.exception(
                f"Failed to send missed holidays to {channel_id}: {e}"
            )
