# commands/holidays_cmd.py

import os
import json
import discord
from discord.ext import commands
from datetime import datetime

from core.holidays_flags import COUNTRY_FLAGS, RELIGION_FLAGS


def load_all_holidays():
    """Load all holidays from every JSON file inside data/holidays/."""
    holidays = []

    base_path = "data/holidays/"
    for filename in os.listdir(base_path):
        if filename.endswith(".json"):
            full_path = os.path.join(base_path, filename)

            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # supports {"holidays": [...]} or raw list
            if isinstance(data, dict) and "holidays" in data:
                holidays.extend(data["holidays"])
            elif isinstance(data, list):
                holidays.extend(data)

    return holidays


def get_next_holiday():
    """Return the closest upcoming holiday from JSON files."""
    today = datetime.now()
    year = today.year

    holidays = load_all_holidays()
    upcoming = []

    for h in holidays:
        mm, dd = h["date"].split("-")
        date = datetime(year, int(mm), int(dd))

        # If this year's date already passed, move to next year
        if date < today:
            date = date.replace(year=year + 1)

        upcoming.append((date, h))

    # sort by actual date
    upcoming.sort(key=lambda x: x[0])

    return upcoming[0]


def build_embed(holiday_date, holiday):
    """Formats one holiday into a Discord embed."""
    mmdd = holiday["date"]
    name = holiday["name"]

    # pick flag
    flag = ""
    if "countries" in holiday:
        flag = COUNTRY_FLAGS.get(holiday["countries"][0], "")
    elif "religion" in holiday:
        flag = RELIGION_FLAGS.get(holiday["religion"], "")

    embed = discord.Embed(
        title="🎉 Next Holiday",
        description=f"{flag} **{name}**\n📅 Date: `{mmdd}`",
        color=0x00ff99
    )
    return embed


def setup(bot):
    @bot.command(name="holidays")
    async def holidays_cmd(ctx):
        holiday_date, holiday = get_next_holiday()
        embed = build_embed(holiday_date, holiday)
        await ctx.send(embed=embed)
