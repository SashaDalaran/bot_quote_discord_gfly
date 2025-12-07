import os
import json
from datetime import datetime

import discord
from discord.ext import commands

from core.dynamic_holidays import get_dynamic_holidays
from core.holidays_flags import COUNTRY_FLAGS

HOLIDAYS_PATH = "data/holidays"


def load_all_holidays():
    today = datetime.now().date()
    holidays = []

    # ===== 1. JSON-файлы =====
    for filename in sorted(os.listdir(HOLIDAYS_PATH)):
        if not filename.endswith(".json"):
            continue

        full_path = os.path.join(HOLIDAYS_PATH, filename)

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            mmdd = entry["date"]
            parsed = datetime.strptime(f"{today.year}-{mmdd}", "%Y-%m-%d").date()

            # Если праздник уже прошёл — перенос на следующий год
            if parsed < today:
                parsed = parsed.replace(year=today.year + 1)

            holidays.append(
                {
                    "date": mmdd,
                    "name": entry["name"],
                    "countries": entry.get("countries", []),
                    "source": filename,
                    "parsed_date": parsed,
                }
            )

    # ===== 2. Dynamic holidays =====
    dyn_list = get_dynamic_holidays()
    for d in dyn_list:
        full_date = datetime.strptime(d["full_date"], "%Y-%m-%d").date()

        holidays.append(
            {
                "date": d["date"],
                "name": d["name"],
                "countries": d.get("countries", []),
                "source": "dynamic_holidays.py",
                "parsed_date": full_date,
            }
        )

    holidays.sort(key=lambda h: h["parsed_date"])
    return holidays


def get_next_for_source(source_name, holidays):
    today = datetime.now().date()
    relevant = [h for h in holidays if h["source"] == source_name]
    upcoming = [h for h in relevant if h["parsed_date"] >= today]

    if not upcoming:
        return None

    return sorted(upcoming, key=lambda h: h["parsed_date"])[0]


@commands.command(name="holidays")
async def holidays_cmd(ctx):
    """Diagnostic command: show nearest holiday for every file."""
    holidays = load_all_holidays()

    embed = discord.Embed(
        title="📅 Nearest Holidays by Source",
        color=0x00AEEF
    )

    # ===== 1. Dynamic ALWAYS first =====
    dyn = get_next_for_source("dynamic_holidays.py", holidays)

    if dyn:
        embed.add_field(
            name="📁 dynamic_holidays.py",
            value=f"🌍 **{dyn['name']}**\n📅 {dyn['date']}",
            inline=False,
        )
    else:
        embed.add_field(
            name="📁 dynamic_holidays.py",
            value="❌ No upcoming holidays",
            inline=False,
        )

    # ===== 2. JSON files =====
    try:
        files = [f for f in os.listdir(HOLIDAYS_PATH) if f.endswith(".json")]
    except FileNotFoundError:
        return await ctx.send("❌ Error: holidays folder not found on server.")

    for filename in sorted(files, key=lambda x: x.lower()):
        next_h = get_next_for_source(filename, holidays)

        if next_h:
            # выберем страну
            country = (
                next_h.get("country")
                or (next_h.get("countries")[0] if next_h.get("countries") else "")
            )

            flag = COUNTRY_FLAGS.get(country, "🌍")

            embed.add_field(
                name=f"📁 {filename}",
                value=f"{flag} **{next_h['name']}**\n📅 {next_h['parsed_date'].strftime('%m-%d')}",
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
