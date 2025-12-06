from datetime import datetime, timezone, timedelta

import discord
from discord.ext import tasks

from core.timers import date_timers, delete_timer, save as save_all_timers
from core.helpers import choose_update_interval, format_remaining


@tasks.loop(seconds=1)
async def update_timers_loop():
    """
    Background loop updating all active date timers.
    The bot instance is attached via update_timers_loop.bot (see bot.py).
    """
    bot = getattr(update_timers_loop, "bot", None)
    if bot is None:
        return

    for timer_id, t in list(date_timers.items()):
        channel = bot.get_channel(t["channel_id"])
        if not channel:
            continue

        try:
            msg = await channel.fetch_message(t["message_id"])
        except Exception:
            continue

        tz = timezone(timedelta(hours=t["tz_offset"]))
        now_local = datetime.now(tz)
        remaining = t["target_timestamp"] - int(now_local.timestamp())

        # Timer finished
        if remaining <= 0:
            embed = discord.Embed(
                title="🎊 The event has started!",
                description=t["text"],
                color=discord.Color.green(),
            )
            await msg.edit(embed=embed)

            if t.get("pinned"):
                try:
                    await msg.unpin()
                except:
                    pass

            delete_timer(timer_id)
            save_all_timers()
            continue

        # Change update interval
        update_timers_loop.change_interval(
            seconds=choose_update_interval(remaining)
        )

        # Update countdown
        embed = discord.Embed(
            title=f"⏳ Timer: {t['text']}",
            description=f"Time left:\n\n**{format_remaining(remaining)}**",
            color=discord.Color.orange(),
        )
        await msg.edit(embed=embed)
