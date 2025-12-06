import os
import json
import logging
from datetime import datetime

import discord
from discord.ext import commands

from core.holiday_flags import COUNTRY_FLAGS, RELIGION_FLAGS

logger = logging.getLogger("holidays_cmd")

HOLIDAYS_PATH = "daily/holidays/data"


def load_all_holidays():
    """Loads holidays from ALL json files in the holidays folder."""
    all_holidays = []

    for filename in os.listdir(HOLIDAYS_PATH):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(HOLIDAYS_PATH, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for h in data:
                # Normalize: add flag from countries OR default 🌍
                countries = h.get("countries", ["world"])
                country = countries[0]

                flag = COUNTRY_FLAGS.get(country, "🌍")

                all_holidays.append({
                    "date": h["date"],
                    "name": h["name"],
                    "flag": flag,
                    "raw": h,
                })

        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")

    return all_holidays


def next_upcoming_holidays(limit=3):
    """Returns the next N upcoming holidays across all files."""
    today = datetime.now().date()

    holidays = load_all_holidays()
    results = []

    for h in holidays:
        try:
            month, day = map(int, h["date"].split("-"))
            holiday_date = datetime(today.year, month, day).date()

            # If date already passed → move to next year
            if holiday_date < today:
                holiday_date = datetime(today.year + 1, month, day).date()

            results.append((holiday_date, h))

        except Exception as e:
            logger.warning(f"Bad date in {h}: {e}")

    results.sort(key=lambda x: x[0])

    return results[:limit]


def setup(bot: commands.Bot):
    @bot.command(name="holidays")
    async def cmd_holidays(ctx: commands.Context):
        upcoming = next_upcoming_holidays(3)

        if not upcoming:
            return await ctx.send("No upcoming holidays found.")

        embed = discord.Embed(
            title="🎉 Next Holidays",
            color=discord.Color.green()
        )

        for date, h in upcoming:
            embed.add_field(
                name=f"{h['flag']} {h['name']}",
                value=f"📅 Date: **{h['date']}**",
                inline=False
            )

        await ctx.send(embed=embed)
