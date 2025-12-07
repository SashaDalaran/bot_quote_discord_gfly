import os
import json
import logging
from datetime import datetime, timedelta, timezone, time

import discord
from discord.ext import tasks

from commands.holidays_cmd import load_all_holidays
from core.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

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


def build_flag(h):
    """Определить страну/религию и вернуть эмодзи-флаг."""
    country = (
        h.get("country")
        or (h.get("countries")[0] if h.get("countries") else "")
    )
    return COUNTRY_FLAGS.get(country, "🌍")


def build_category_line(h):
    """Собрать строку для value: категория + эмодзи."""
    categories = h.get("categories", [])
    if not categories:
        return ""

    main_cat = categories[0]
    cat_emoji = CATEGORY_EMOJIS.get(main_cat, "")
    if cat_emoji:
        return f"{cat_emoji} `{main_cat}`"
    else:
        return f"`{main_cat}`"

def get_flag_for_holiday(h):
    country = ""
    if h.get("country"):
        country = h["country"]
    elif h.get("countries"):
        country = h["countries"][0]
    return COUNTRY_FLAGS.get(country, "🌍")


def get_category_line(h):
    categories = h.get("categories") or []
    if not categories:
        return ""

    main = categories[0]
    emoji = CATEGORY_EMOJIS.get(main)
    if not emoji:
        return main  # просто текст категории, если эмодзи нет

    return f"{emoji} {main}"


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
            flag = build_flag(h)
            value = build_category_line(h)

            embed.add_field(
                name=f"{flag} {h['name']}",
                value=value,
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

    # Если время уже прошло сегодня -> отправляем один раз сейчас
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
                flag = build_flag(h)
                value = build_category_line(h)

                embed.add_field(
                    name=f"{flag} {h['name']}",
                    value=value,
                    inline=False,
                )

            try:
                await channel.send(embed=embed)
                logger.info(f"Sent missed holidays to {channel_id}")
            except Exception as e:
                logger.exception(f"Failed to send missed holidays to {channel_id}: {e}")
