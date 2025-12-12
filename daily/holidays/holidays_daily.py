import os
import logging
from datetime import datetime, timedelta, timezone, time

import discord
from discord.ext import tasks

from commands.holidays_cmd import load_all_holidays
from core.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

logger = logging.getLogger("holidays_daily")

# Timezone: GMT+3
TZ = timezone(timedelta(hours=3))

# List of channel IDs from environment
HOLIDAYS_CHANNEL_IDS = [
    cid.strip()
    for cid in os.getenv("HOLIDAYS_CHANNEL_IDS", "").split(",")
    if cid.strip().isdigit()
]


def is_today(h):
    """Return True if the holiday matches today's date."""
    today = datetime.now(TZ).date()
    return h.get("parsed_date") == today


def build_flag(h):
    """Return emoji flag for holiday country."""
    country = (
        h.get("country")
        or (h.get("countries")[0] if h.get("countries") else "")
    )
    return COUNTRY_FLAGS.get(country, "🌍")


def build_category_line(h):
    """Return first category with emoji."""
    categories = h.get("categories") or []
    if not categories:
        return ""

    main = categories[0]
    emoji = CATEGORY_EMOJIS.get(main, "")
    return f"{emoji} `{main}`" if emoji else f"`{main}`"


# ======================================================
# DAILY HOLIDAYS TASK @ 10:01 (GMT+3)
# ======================================================
@tasks.loop(time=time(hour=10, minute=1, tzinfo=TZ))
async def send_holidays_daily():
    """Daily holidays sender."""
    bot = send_holidays_daily.bot  # injected from bot.py
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
                value=build_category_line(h),
                inline=False,
            )

        try:
            await channel.send(embed=embed)
            logger.info(f"Sent daily holidays to {channel_id}")
        except Exception as e:
            logger.exception(f"Failed to send to {channel_id}: {e}")


# ======================================================
# "SEND ONCE IF MISSED" (bot restart after 10:01)
# ======================================================
async def send_once_if_missed_holidays():
    """Send holidays once if bot missed the scheduled time."""
    bot = send_once_if_missed_holidays.bot  # injected from bot.py

    now = datetime.now(TZ)
    scheduled = now.replace(hour=10, minute=1, second=0, microsecond=0)

    # If now is after 10:01 => send once
    if now <= scheduled:
        return

    holidays = load_all_holidays()
    todays = [h for h in holidays if is_today(h)]

    if not todays:
        logger.info("No holidays today (missed check).")
        return

    logger.info("Missed scheduled time — sending holiday list once now...")

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
                value=build_category_line(h),
                inline=False,
            )

        try:
            await channel.send(embed=embed)
            logger.info(f"Sent missed holidays to {channel_id}")
        except Exception as e:
            logger.exception(f"Failed to send missed holidays to {channel_id}: {e}")
