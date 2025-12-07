import os
import json
import logging
from datetime import datetime, timedelta, timezone, time

import discord
from discord.ext import tasks

from commands.holidays_cmd import load_all_holidays

logger = logging.getLogger("holidays_daily")

TZ = timezone(timedelta(hours=3))  # GMT+3

HOLIDAYS_CHANNEL_IDS = [
    cid.strip()
    for cid in os.getenv("HOLIDAYS_CHANNEL_IDS", "").split(",")
    if cid.strip().isdigit()
]


def is_today(h):
    """Check via parsed_date from load_all_holidays()"""
    today = datetime.now(TZ).date()
    return h["parsed_date"] == today


@tasks.loop(time=time(hour=10, minute=1, tzinfo=TZ))
async def send_holidays_daily(bot):
    """Runs daily at 10:01 GMT+3."""
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
            # Determine flag
            country = ""
            if "country" in h:
                country = h["country"]
            elif "countries" in h and h["countries"]:
                country = h["countries"][0]

            flag = h.get("flag") or "🌍"

            embed.add_field(
                name=f"{flag} {h['name']}",
                value="",   # No category
                inline=False,
            )

        try:
            await channel.send(embed=embed)
            logger.info(f"Sent holidays to channel {channel_id}")
        except Exception as e:
            logger.exception(f"Failed to send to {channel_id}: {e}")


async def send_once_if_missed_holidays(bot):
    """If bot was offline at 10:01, send once on startup."""
    now = datetime.now(TZ)
    target_time = now.replace(hour=10, minute=1, second=0, microsecond=0)

    # If time already passed today -> send once now
    if now > target_time:
        logger.info("Missed daily holidays time — sending once now...")

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
                flag = h.get("flag") or "🌍"
                embed.add_field(
                    name=f"{flag} {h['name']}",
                    value="",
                    inline=False,
                )

            try:
                await channel.send(embed=embed)
                logger.info(f"Sent missed holidays to {channel_id}")
            except Exception as e:
                logger.exception(f"Failed to send missed holidays to {channel_id}: {e}")
