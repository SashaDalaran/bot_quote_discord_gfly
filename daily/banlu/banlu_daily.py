import os
import random
from datetime import datetime, timedelta, timezone, time

import discord
from discord.ext import tasks

# Timezone for sending Ban'Lu quotes
TZ = timezone(timedelta(hours=3))

# Path to quotes file
BANLU_FILE = os.getenv("BANLU_QUOTES_FILE", "data/quotersbanlu.txt")

# Channel ID
BANLU_CHANNEL_ID = int(os.getenv("BANLU_CHANNEL_ID", "0"))


def load_banlu_quotes():
    """Load Ban'Lu quotes from file."""
    if not os.path.exists(BANLU_FILE):
        return []
    with open(BANLU_FILE, "r", encoding="utf-8") as f:
        return [x.strip() for x in f.readlines() if x.strip()]


# Loaded once at startup
banlu_quotes = load_banlu_quotes()


# ============================
# Daily Ban'Lu task (10:00)
# ============================
@tasks.loop(time=time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily():
    bot = send_banlu_daily.bot  # injected from bot.py

    if not banlu_quotes:
        return

    channel = bot.get_channel(BANLU_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="🏌️ Daily Quote • Ban'Lu",
        description=random.choice(banlu_quotes),
        color=discord.Color.gold()
    )
    embed.set_footer(text=datetime.now(TZ).strftime("%d.%m.%Y"))

    await channel.send(embed=embed)


# ============================================================
# One-time catch-up (if bot restarted after 10:00)
# ============================================================
async def send_once_if_missed():
    bot = send_once_if_missed.bot  # injected from bot.py

    now = datetime.now(TZ)
    target = now.replace(hour=10, minute=0, second=0, microsecond=0)

    # If already past 10:00 — send once
    if now > target:
        channel = bot.get_channel(BANLU_CHANNEL_ID)
        if channel and banlu_quotes:
            embed = discord.Embed(
                title="🏌️ Daily Quote • Ban'Lu",
                description=random.choice(banlu_quotes),
                color=discord.Color.gold()
            )
            embed.set_footer(text=now.strftime("%d.%m.%Y"))
            await channel.send(embed=embed)
