import os
import json
from datetime import datetime

import discord
from discord.ext import commands

from core.dynamic_holidays import get_dynamic_holidays
from core.holidays_flags import COUNTRY_FLAGS

HOLIDAYS_PATH = "daily/holidays/data"


def load_all_holidays():
    """Loads all holidays from JSON files + dynamic holidays."""
    holidays = []

    # Load static json files
    if os.path.isdir(HOLIDAYS_PATH):
        for filename in sorted(os.listdir(HOLIDAYS_PATH), key=lambda x: x.lower()):
            if filename.endswith(".json"):
                path = os.path.join(HOLIDAYS_PATH, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for h in data:
                            h["source"] = filename
                        holidays.extend(data)
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")

    # Load dynamic holidays
    dynamic = get_dynamic_holidays()
    for h in dynamic:
        h["source"] = "dynamic_holidays.py"
    holidays.extend(dynamic)

    # Sorting all holidays by date
    holidays.sort(key=lambda h: datetime.strptime(h["date"], "%Y-%m-%d"))

    return holidays


def get_next_for_source(source_name, holidays):
    """Returns the nearest upcoming holiday for a given source."""
    today = datetime.now().date()

    relevant = [h for h in holidays if h["source"] == source_name]

    upcoming = [
        h for h in relevant
        if datetime.strptime(h["date"], "%Y-%m-%d").date() >= today
    ]

    if not upcoming:
        return None

    upcoming.sort(key=lambda h: h["date"])
    return upcoming[0]


@commands.command(name="holidays")
async def holidays_cmd(ctx):
    """Diagnostic command: show nearest holiday for every file."""
    holidays = load_all_holidays()

    embed = discord.Embed(
        title="📅 Nearest Holidays by Source",
        color=0x00AEEF
    )

    # --- 1) DYNAMIC ALWAYS FIRST ---
    dyn = get_next_for_source("dynamic_holidays.py", holidays)
    if dyn:
        flag = COUNTRY_FLAGS.get(dyn["country"], "🌍")
        embed.add_field(
            name="📁 dynamic_holidays.py",
            value=(
                f"{flag} **{dyn['name']}**\n"
                f"📅 {datetime.strptime(dyn['date'], '%Y-%m-%d').strftime('%m-%d')}"
            ),
            inline=False,
        )
    else:
        embed.add_field(
            name="📁 dynamic_holidays.py",
            value="❌ No upcoming holidays",
            inline=False,
        )

    # --- 2) Now all JSON files, alphabetically ---
    files = [
        f for f in os.listdir(HOLIDAYS_PATH)
        if f.endswith(".json")
    ]

    for filename in sorted(files, key=lambda x: x.lower()):
        next_h = get_next_for_source(filename, holidays)

        if next_h:
            flag = COUNTRY_FLAGS.get(next_h["country"], "🌍")

            embed.add_field(
                name=f"📁 {filename}",
                value=(
                    f"{flag} **{next_h['name']}**\n"
                    f"📅 {datetime.strptime(next_h['date'], '%Y-%m-%d').strftime('%m-%d')}"
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name=f"📁 {filename}",
                value="❌ No upcoming holidays",
                inline=False,
            )

    await ctx.send(embed=embed)

def setup(bot):
    bot.add_command(holidays_cmd)
