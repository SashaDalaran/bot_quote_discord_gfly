import os
import json
from datetime import datetime

import discord
from discord.ext import commands

from core.dynamic_holidays import get_dynamic_holidays
from core.holidays_flags import COUNTRY_FLAGS, RELIGION_FLAGS

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Folder with holiday JSON files
HOLIDAYS_PATH = os.path.join(BASE_DIR, "data", "holidays")


def load_holidays_from_file(path: str):
    """Load holidays from one JSON file. 
    If error — return dict with 'error'."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def get_next_from_list(holidays: list):
    """Return the closest upcoming holiday from a list."""
    today = datetime.now()
    year = today.year
    parsed = []

    for h in holidays:
        try:
            mm, dd = h["date"].split("-")
            date_obj = datetime(year, int(mm), int(dd))

            # If this year's date already passed → move to next year
            if date_obj < today:
                date_obj = date_obj.replace(year=year + 1)
            parsed.append((date_obj, h))
        except Exception:
            continue

    if not parsed:
        return None

    # 👉 Sorting by nearest date (closest first)
    parsed.sort(key=lambda x: x[0])
    return parsed[0]


def get_flag(holiday: dict) -> str:
    """Choose flag emoji based on country or religion."""
    if holiday.get("countries"):
        return COUNTRY_FLAGS.get(holiday["countries"][0], "")
    if holiday.get("religion"):
        return RELIGION_FLAGS.get(holiday["religion"], "")
    return ""


def setup(bot: commands.Bot):
    @bot.command(name="holidays", help="Show closest holiday from every JSON file.")
    async def holidays_cmd(ctx: commands.Context):
        """
        Admin diagnostic command.
        For every JSON file in /data/holidays, show the nearest holiday.
        Purpose: check readability of all holiday files (especially new ones).
        """

        embed = discord.Embed(
            title="🎉 Holiday Files Diagnostic",
            description=(
                "Shows the closest holiday from **each JSON file** in `/data/holidays`.\n"
                "Useful to verify that all holiday files load correctly."
            ),
            color=0x00AEEF,
        )

        # 👉 SORT FILES ALPHABETICALLY HERE
        files = sorted(os.listdir(HOLIDAYS_PATH))

        for filename in files:
            if not filename.endswith(".json"):
                continue

            full_path = os.path.join(HOLIDAYS_PATH, filename)
            data = load_holidays_from_file(full_path)

            # If there was an error reading the file
            if isinstance(data, dict) and "error" in data:
                embed.add_field(
                    name=f"❌ {filename}",
                    value=f"Error reading file:\n`{data['error']}`",
                    inline=False,
                )
                continue

            holidays_list = data  # Only JSON holidays, no dynamic ones for diagnostics

            next_holiday = get_next_from_list(holidays_list)

            if not next_holiday:
                embed.add_field(
                    name=f"⚠️ {filename}",
                    value="No valid holidays found in this file.",
                    inline=False,
                )
                continue

            date_obj, holiday = next_holiday
            mmdd = holiday["date"]
            flag = get_flag(holiday)

            embed.add_field(
                name=f"📁 {filename}",
                value=(
                    f"{flag} **{holiday['name']}**\n"
                    f"📅 File date: `{mmdd}`"
                ),
                inline=False,
            )

        await ctx.send(embed=embed)
