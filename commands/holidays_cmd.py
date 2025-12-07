import os
import json
from datetime import datetime

import discord
from discord.ext import commands

from core.dynamic_holidays import get_dynamic_holidays
from core.holidays_flags import COUNTRY_FLAGS

HOLIDAYS_PATH = "daily/holidays/data"


# ---------- DATE PARSER ----------
def parse_date(date_str):
    """
    Converts MM-DD or YYYY-MM-DD → datetime object (year adjusted to THIS YEAR).
    """
    today_year = datetime.now().year

    # MM-DD format
    if len(date_str) == 5 and date_str[2] == "-":
        return datetime.strptime(f"{today_year}-{date_str}", "%Y-%m-%d")

    # YYYY-MM-DD format
    if len(date_str) == 10 and date_str[4] == "-":
        return datetime.strptime(date_str, "%Y-%m-%d")

    # Fallback
    raise ValueError(f"Unsupported date format: {date_str}")


# ---------- LOADER ----------
def load_all_holidays():
    """Loads static JSON holiday files + dynamic holidays."""
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
                            h["parsed_date"] = parse_date(h["date"])

                        holidays.extend(data)
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")

    # Load dynamic holidays
    dynamic = get_dynamic_holidays()
    for h in dynamic:
        h["source"] = "dynamic_holidays.py"
        h["parsed_date"] = parse_date(h["date"])
    holidays.extend(dynamic)

    return holidays


# ---------- PICK CLOSEST ----------
def get_next_for_source(source_name, holidays):
    """Returns the closest upcoming holiday for a given source."""
    today = datetime.now()

    relevant = [h for h in holidays if h["source"] == source_name]

    upcoming = [h for h in relevant if h["parsed_date"] >= today]

    if not upcoming:
        return None

    return sorted(upcoming, key=lambda h: h["parsed_date"])[0]


# ---------- COMMAND ----------
@commands.command(name="holidays")
async def holidays_cmd(ctx):
    """Diagnostic command: show nearest holidays by file."""
    holidays = load_all_holidays()

    embed = discord.Embed(
        title="📅 Nearest Holidays by Source",
        color=0x00AEEF,
    )

    # --- 1) DYNAMIC FIRST ---
    dyn = get_next_for_source("dynamic_holidays.py", holidays)

    if dyn:
        country = dyn.get("country", "")
        flag = COUNTRY_FLAGS.get(country, "🌍")

        embed.add_field(
            name="📁 dynamic_holidays.py",
            value=(
                f"{flag} **{dyn['name']}**\n"
                f"📅 {dyn['parsed_date'].strftime('%m-%d')}"
            ),
            inline=False,
        )
    else:
        embed.add_field(
            name="📁 dynamic_holidays.py",
            value="❌ No upcoming holidays",
            inline=False,
        )

    # --- 2) STATIC JSON FILES ---
    files = [
        f for f in os.listdir(HOLIDAYS_PATH)
        if f.endswith(".json")
    ]

    for filename in sorted(files, key=lambda x: x.lower()):
        next_h = get_next_for_source(filename, holidays)

        if next_h:
            country = next_h.get("country", "")
            flag = COUNTRY_FLAGS.get(country, "🌍")

            embed.add_field(
                name=f"📁 {filename}",
                value=(
                    f"{flag} **{next_h['name']}**\n"
                    f"📅 {next_h['parsed_date'].strftime('%m-%d')}"
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