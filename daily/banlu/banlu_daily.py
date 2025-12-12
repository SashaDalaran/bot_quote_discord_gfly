# ==================================================
# daily/banlu/banlu_daily.py — Daily Ban’Lu Quote
# ==================================================

import os
import random
from datetime import datetime, timedelta, timezone, time

import discord
from discord.ext import tasks


# ===========================
# Configuration
# ===========================
TZ = timezone(timedelta(hours=3))  # GMT+3 timezone
BANLU_FILE = os.getenv("BANLU_QUOTES_FILE", "data/quotersbanlu.txt")
BANLU_CHANNEL_ID = int(os.getenv("BANLU_CHANNEL_ID", "0"))


# ===========================
# Load Quotes
# ===========================
def load_banlu_quotes() -> list[str]:
    """Load Ban’Lu quotes from file and return a cleaned list."""
    if not os.path.exists(BANLU_FILE):
        return []

    with open(BANLU_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


# Preload quotes once at startup
banlu_quotes = load_banlu_quotes()


# ===========================
# Daily Scheduled Task (10:00 GMT+3)
# ===========================
@tasks.loop(time=time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily():
    """
    Automatically send a Ban’Lu quote every day at 10:00 GMT+3.
    The bot reference is injected via `bot.py`.
    """
    bot = send_banlu_daily.bot  # injected externally

    if not banlu_quotes:
        return

    channel = bot.get_channel(BANLU_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="🏌️ Daily Quote • Ban'Lu",
        description=random.choice(banlu_quotes),
        color=discord.Color.gold(),
    )
    embed.set_footer(text=datetime.now(TZ).strftime("%d.%m.%Y"))

    await channel.send(embed=embed)


# ==================================================
# One-Time Catch-Up (if bot restarted after 10:00)
# ==================================================
async def send_once_if_missed():
    """
    If the bot was offline at 10:00, send the Ban’Lu quote once
    when the bot restarts later in the day.
    """
    bot = send_once_if_missed.bot  # injected externally

    now = datetime.now(TZ)
    target = now.replace(hour=10, minute=0, second=0, microsecond=0)

    # If it's already past 10:00 → send the quote once
    if now > target and banlu_quotes:
        channel = bot.get_channel(BANLU_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="🏌️ Daily Quote • Ban'Lu",
                description=random.choice(banlu_quotes),
                color=discord.Color.gold(),
            )
            embed.set_footer(text=now.strftime("%d.%m.%Y"))
            await channel.send(embed=embed)
