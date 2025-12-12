# ==================================================
# core/timer_engine.py — Real-Time Timer Update Loop
# ==================================================

from datetime import datetime, timezone, timedelta

import discord
from discord.ext import tasks

from core.timers import date_timers, delete_timer, save as save_all_timers
from core.helpers import choose_update_interval, format_remaining


# ===========================
# Background Timer Update Loop
# ===========================
@tasks.loop(seconds=1)
async def update_timers_loop():
    """
    Background loop that updates all active date timers.
    The bot instance is injected externally via:
        update_timers_loop.bot = bot
    """
    bot = getattr(update_timers_loop, "bot", None)
    if bot is None:
        return

    # Iterate over a copy since timer removal may occur
    for timer_id, t in list(date_timers.items()):
        channel = bot.get_channel(t["channel_id"])
        if not channel:
            continue

        # -------------------------------------------
        # Fetch the target message
        # -------------------------------------------
        try:
            msg = await channel.fetch_message(t["message_id"])
        except Exception:
            # Message deleted or inaccessible
            continue

        # -------------------------------------------
        # Time Calculation
        # -------------------------------------------
        tz = timezone(timedelta(hours=t["tz_offset"]))
        now_local = datetime.now(tz)
        remaining = t["target_timestamp"] - int(now_local.timestamp())

        # ===========================
        # Timer Reached Zero
        # ===========================
        if remaining <= 0:
            embed = discord.Embed(
                title="🎊 The event has started!",
                description=t["text"],
                color=discord.Color.green(),
            )
            await msg.edit(embed=embed)

            # Unpin if originally pinned
            if t.get("pinned"):
                try:
                    await msg.unpin()
                except Exception:
                    pass

            delete_timer(timer_id)
            save_all_timers()
            continue

        # ===========================
        # Adjust Update Frequency
        # ===========================
        update_timers_loop.change_interval(
            seconds=choose_update_interval(remaining)
        )

        # ===========================
        # Update Countdown Message
        # ===========================
        embed = discord.Embed(
            title=f"⏳ Timer: {t['text']}",
            description=f"Time left:\n\n**{format_remaining(remaining)}**",
            color=discord.Color.orange(),
        )

        try:
            await msg.edit(embed=embed)
        except Exception:
            # If editing fails (permissions / deleted message), skip silently
            continue
