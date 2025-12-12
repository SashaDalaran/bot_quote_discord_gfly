# ==================================================
# commands/holidays_cmd.py — Holiday Lookup Command
# ==================================================

import os
import json
from datetime import datetime

import discord
from discord.ext import commands

from core.dynamic_holidays import get_dynamic_holidays
from core.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

HOLIDAYS_PATH = "data/holidays"


# ===========================
# Load All Holidays (Static JSON + Dynamic)
# ===========================
def load_all_holidays():
    """
    Load all holidays from JSON files and dynamic holiday sources.
    Normalizes categories and maps holiday dates to their next occurrence.
    """
    today = datetime.now().date()
    holidays = []

    # -------------------------------------------
    # 1. Load static holidays from JSON files
    # -------------------------------------------
    for filename in sorted(os.listdir(HOLIDAYS_PATH)):
        if not filename.endswith(".json"):
            continue

        full_path = os.path.join(HOLIDAYS_PATH, filename)

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            mmdd = entry["date"]

            # Construct YYYY-MM-DD from this year
            parsed_date = datetime.strptime(
                f"{today.year}-{mmdd}", "%Y-%m-%d"
            ).date()

            # If holiday already passed this year → shift to next year
            if parsed_date < today:
                parsed_date = parsed_date.replace(year=today.year + 1)

            # Normalize category field
            categories = (
                entry.get("category")
                or entry.get("categories")
                or []
            )
            if isinstance(categories, str):
                categories = [categories]

            holidays.append(
                {
                    "date": mmdd,
                    "name": entry["name"],
                    "countries": entry.get("countries", []),
                    "categories": categories,
                    "source": filename,
                    "parsed_date": parsed_date,
                }
            )

    # -------------------------------------------
    # 2. Add dynamic holidays (e.g., Easters)
    # -------------------------------------------
    dynamic_list = get_dynamic_holidays()
    for d in dynamic_list:
        full_date = datetime.strptime(d["full_date"], "%Y-%m-%d").date()

        holidays.append(
            {
                "date": d["date"],
                "name": d["name"],
                "countries": d.get("countries", []),
                "categories": d.get("categories", d.get("category", [])),
                "source": "dynamic_holidays.py",
                "parsed_date": full_date,
            }
        )

    # -------------------------------------------
    # Sort by nearest date
    # -------------------------------------------
    holidays.sort(key=lambda h: h["parsed_date"])
    return holidays


# ===========================
# Get Nearest Holiday For a Given Source File
# ===========================
def get_next_for_source(source_name, holidays):
    """
    Return the nearest upcoming holiday for a given source file.
    """
    today = datetime.now().date()
    relevant = [h for h in holidays if h["source"] == source_name]
    upcoming = [h for h in relevant if h["parsed_date"] >= today]

    if not upcoming:
        return None

    return sorted(upcoming, key=lambda h: h["parsed_date"])[0]


# ===========================
# Category Line Builder
# Adds emoji if available
# ===========================
def build_category_line_for_cmd(h):
    categories = h.get("categories", [])
    if not categories:
        return ""

    main = categories[0]
    emoji = CATEGORY_EMOJIS.get(main, "")

    return f"{emoji} {main}" if emoji else main


# ===========================
# Command: !holidays
# Show nearest holiday per source file
# ===========================
@commands.command(name="holidays")
async def holidays_cmd(ctx):
    """Diagnostic command: show nearest holiday for each source file."""

    holidays = load_all_holidays()

    embed = discord.Embed(
        title="📅 Nearest Holidays by Source",
        color=0x00AEEF,
    )

    # -------------------------------------------
    # 1. Dynamic Holidays (always shown first)
    # -------------------------------------------
    dyn = get_next_for_source("dynamic_holidays.py", holidays)

    if dyn:
        cat_line = build_category_line_for_cmd(dyn)
        if cat_line:
            value = (
                f"🌍 **{dyn['name']}**\n"
                f"{cat_line}\n"
                f"📅 {dyn['date']}"
            )
        else:
            value = (
                f"🌍 **{dyn['name']}**\n"
                f"📅 {dyn['date']}"
            )

        embed.add_field(
            name="📁 dynamic_holidays.py",
            value=value,
            inline=False,
        )
    else:
        embed.add_field(
            name="📁 dynamic_holidays.py",
            value="❌ No upcoming holidays",
            inline=False,
        )

    # -------------------------------------------
    # 2. Static JSON Files
    # -------------------------------------------
    try:
        files = [
            f for f in os.listdir(HOLIDAYS_PATH)
            if f.endswith(".json")
        ]
    except FileNotFoundError:
        return await ctx.send("❌ Error: holidays folder not found on server.")

    for filename in sorted(files, key=lambda x: x.lower()):
        next_h = get_next_for_source(filename, holidays)

        if next_h:
            # Use first country if available
            country = (
                next_h.get("country")
                or (next_h["countries"][0] if next_h.get("countries") else "")
            )
            flag = COUNTRY_FLAGS.get(country, "🌍")

            cat_line = build_category_line_for_cmd(next_h)

            if cat_line:
                value = (
                    f"{flag} **{next_h['name']}**\n"
                    f"{cat_line}\n"
                    f"📅 {next_h['parsed_date'].strftime('%m-%d')}"
                )
            else:
                value = (
                    f"{flag} **{next_h['name']}**\n"
                    f"📅 {next_h['parsed_date'].strftime('%m-%d')}"
                )

            embed.add_field(
                name=f"📁 {filename}",
                value=value,
                inline=False,
            )

        else:
            embed.add_field(
                name=f"📁 {filename}",
                value="❌ No upcoming holidays",
                inline=False,
            )

    await ctx.send(embed=embed)


# ===========================
# Registration Hook
# ===========================
def setup(bot):
    bot.add_command(holidays_cmd)
