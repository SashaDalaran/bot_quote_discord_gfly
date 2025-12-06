# commands/holidays_cmd.py

import os
import json
import discord
from discord.ext import commands
from datetime import datetime

from core.holidays_flags import COUNTRY_FLAGS, RELIGION_FLAGS
from core.dynamic_holidays import get_dynamic_holidays


def load_all_holidays():
    """Loads all holidays from every JSON file inside data/holidays/ folder."""
    holidays = []

    # динамические праздники (Пасха, Рамадан и т.п.)
    holidays.extend(get_dynamic_holidays())

    base_path = "data/holidays/"
    for filename in os.listdir(base_path):
        if filename.endswith(".json"):
            full_path = os.path.join(base_path, filename)

            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # поддерживаем {"holidays": [...]} или просто список
            if isinstance(data, dict) and "holidays" in data:
                holidays.extend(data["holidays"])
            elif isinstance(data, list):
                holidays.extend(data)

    return holidays


def get_next_holiday():
    """Returns the closest upcoming holiday."""
    today = datetime.now()
    year = today.year

    holidays = load_all_holidays()
    upcoming = []

    for h in holidays:
        mm, dd = h["date"].split("-")
        holiday_date = datetime(year, int(mm), int(dd))

        # если в этом году уже прошло — переносим на следующий
        if holiday_date < today:
            holiday_date = holiday_date.replace(year=year + 1)

        upcoming.append((holiday_date, h))

    upcoming.sort(key=lambda x: x[0])
    return upcoming[0]


def build_embed(holiday_date, holiday):
    """Formats embed message for Discord."""
    mmdd = holiday["date"]
    name = holiday["name"]

    flag = ""
    if "countries" in holiday and holiday["countries"]:
        c = holiday["countries"][0]
        flag = COUNTRY_FLAGS.get(c, "")
    elif "religion" in holiday and holiday.get("religion"):
        flag = RELIGION_FLAGS.get(holiday["religion"], "")

    embed = discord.Embed(
        title="🎉 Next Holiday",
        description=f"{flag} **{name}**\n📅 Date: `{mmdd}`\n(closest occurrence)",
        color=0x00FF99,
    )
    return embed


def setup(bot: commands.Bot):
    @bot.command(
        name="holidays",
        aliases=["holiday", "today", "next"],
        help="Shows the next upcoming holiday across all JSON files.",
    )
    async def holidays_cmd(ctx: commands.Context):
        holiday_date, holiday = get_next_holiday()
        embed = build_embed(holiday_date, holiday)
        await ctx.send(embed=embed)
