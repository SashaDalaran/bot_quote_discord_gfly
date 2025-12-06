# daily/holidays/holidays_daily.py

import os
from datetime import datetime, timezone, timedelta, time

import discord
from discord.ext import tasks

from commands.holidays_cmd import load_all_holidays
from core.holidays_flags import COUNTRY_FLAGS, RELIGION_FLAGS
from core.dynamic_holidays import get_dynamic_holidays   # ← added

TZ = timezone(timedelta(hours=3))

HOLIDAYS_CHANNELS = os.getenv("HOLIDAYS_CHANNELS", "")


def get_today_holidays():
    """Return today's holidays including dynamic ones."""
    today = datetime.now(TZ).strftime("%m-%d")

    holidays = load_all_holidays()
    holidays.extend(get_dynamic_holidays())   # ← dynamic holidays included here

    return [h for h in holidays if h["date"] == today]


def build_embeds(holidays):
    embeds = []
    groups = {}

    for h in holidays:
        if "countries" in h:
            key = h["countries"][0]
            label = COUNTRY_FLAGS.get(key, "🌍")
        else:
            key = h["religion"]
            label = RELIGION_FLAGS.get(key, "✨")

        if key not in groups:
            groups[key] = {"label": label, "items": []}

        groups[key]["items"].append(h)

    for key, group in groups.items():
        embed = discord.Embed(
            title=f"{group['label']} Holidays Today",
            color=0x00ff99
        )
        for h in group["items"]:
            embed.add_field(name=h["name"], value=f"📅 {h['date']}", inline=False)

        embed.set_footer(text=datetime.now(TZ).strftime("%d.%m.%Y"))
        embeds.append(embed)

    return embeds


@tasks.loop(time=time(hour=10, minute=1, tzinfo=TZ))
async def send_holidays_daily():
    raw = HOLIDAYS_CHANNELS
    if not raw:
        return

    channels = [int(x) for x in raw.split(",") if x.strip()]
    holidays_today = get_today_holidays()
    if not holidays_today:
        return

    bot = send_holidays_daily.bot
    embeds = build_embeds(holidays_today)

    for ch in channels:
        channel = bot.get_channel(ch)
        if channel:
            for embed in embeds:
                await channel.send(embed=embed)


async def send_once_if_missed_holidays(bot):
    now = datetime.now(TZ)
    target = now.replace(hour=10, minute=1, second=0, microsecond=0)

    if now <= target:
        return

    raw = HOLIDAYS_CHANNELS
    if not raw:
        return

    channels = [int(x) for x in raw.split(",") if x.strip()]
    holidays_today = get_today_holidays()
    if not holidays_today:
        return

    embeds = build_embeds(holidays_today)

    for ch in channels:
        channel = bot.get_channel(ch)
        if channel:
            for embed in embeds:
                await channel.send(embed=embed)
