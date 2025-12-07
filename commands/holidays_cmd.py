import os
import json
from datetime import datetime, date

import discord
from discord.ext import commands

from core.dynamic_holidays import get_dynamic_holidays
from core.holidays_flags import COUNTRY_FLAGS

HOLIDAYS_PATH = "daily/holidays/data"


# ===============================
#   DATE PARSER (supports MM-DD)
# ===============================
def parse_date(date_str: str) -> date:
    """
    Accepts:
      • YYYY-MM-DD
      • MM-DD   (auto-assigned to this or next year)
    Returns: datetime.date
    """

    today = datetime.now().date()

    # Format MM-DD (length 5 → "04-20")
    if len(date_str) == 5 and date_str[2] == "-":
        month = int(date_str[:2])
        day = int(date_str[3:])

        year = today.year
        parsed = date(year, month, day)

        # если праздник уже прошёл — переносим на следующий год
        if parsed < today:
            parsed = date(year + 1, month, day)

        return parsed

    # Format YYYY-MM-DD
    return datetime.strptime(date_str, "%Y-%m-%d").date()


# ===============================
#      LOAD ALL HOLIDAYS
# ===============================
def load_all_holidays():
    """Load all JSON holidays + dynamic holidays."""
    holidays = []

    # Static JSON files
    if os.path.isdir(HOLIDAYS_PATH):
        for filename in sorted(os.listdir(HOLIDAYS_PATH), key=lambda x: x.lower()):
            if filename.endswith(".json"):
                full_path = os.path.join(HOLIDAYS_PATH, filename)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                        for h in data:
                            h["source"] = filename
                            h["parsed_date"] = parse_date(h["date"])

                        holidays.extend(data)

                except Exception as e:
                    print(f"Failed to load {filename}: {e}")

    # Dynamic holidays
    dynamic = get_dynamic_holidays()
    for h in dynamic:
        h["source"] = "dynamic_holidays.py"
        h["parsed_date"] = parse_date(h["date"])
    holidays.extend(dynamic)

    # Global sort (по дате)
    holidays.sort(key=lambda h: h["parsed_date"])

    return holidays


# ===============================
#   GET NEXT HOLIDAY PER FILE
# ===============================
def get_next_for_source(source_name, holidays):
    today = datetime.now().date()

    relevant = [h for h in holidays if h["source"] == source_name]

    upcoming = [h for h in relevant if h["parsed_date"] >= today]

    if not upcoming:
        return None

    upcoming.sort(key=lambda h: h["parsed_date"])
    return upcoming[0]


# ===============================
#         COMMAND
# ===============================
@commands.command(name="holidays")
async def holidays_cmd(ctx):
    """Diagnostic: show nearest holiday from each file."""
    holidays = load_all_holidays()

    embed = discord.Embed(
        title="📅 Nearest Holidays by Source",
        color=0x00AEEF
    )

    # --- 1) Dynamic ALWAYS first ---
    dyn = get_next_for_source("dynamic_holidays.py", holidays)

    if dyn:
        flag = COUNTRY_FLAGS.get(dyn["country"], "🌍")
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

    # --- 2) JSON files ---
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


# ===============================
#      COMMAND REGISTER
# ===============================
def setup(bot):
    bot.add_command(holidays_cmd)