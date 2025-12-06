import os
import random
from datetime import datetime, timedelta, timezone, time

import discord
from discord.ext import tasks

TZ = timezone(timedelta(hours=3))

BANLU_FILE = os.getenv("BANLU_QUOTES_FILE", "data/quotersbanlu.txt")
BANLU_CHANNEL_ID = int(os.getenv("BANLU_CHANNEL_ID", "0"))


def load_banlu_quotes():
    """Load Ban'Lu quotes from file."""
    if not os.path.exists(BANLU_FILE):
        return []
    with open(BANLU_FILE, "r", encoding="utf-8") as f:
        return [x.strip() for x in f.readlines() if x.strip()]


banlu_quotes = load_banlu_quotes()


@tasks.loop(time=time(hour=10, minute=0, tzinfo=TZ))
async def send_banlu_daily():
    """Send a daily Ban'Lu quote at 10:00 MSK."""
    if not BANLU_CHANNEL_ID or not banlu_quotes:
        return

    bot = send_banlu_daily.bot
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


async def send_once_if_missed(bot):
    """If it's already past 10:00 and the daily quote wasn't sent, send it once."""
    now = datetime.now(TZ)
    target = now.replace(hour=10, minute=0, second=0, microsecond=0)

    # If it's after 10:00 and the quote wasn't sent — send it once
    if now > target:
        channel = bot.get_channel(BANLU_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="🏌️ Daily Quote • Ban'Lu",
                description=random.choice(banlu_quotes),
                color=discord.Color.gold()
            )
            embed.set_footer(text=now.strftime("%d.%m.%Y"))
            await channel.send(embed=embed)
