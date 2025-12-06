# commands/date_timer.py
from datetime import datetime, timedelta, timezone
import os

import discord
from discord.ext import commands

from core.timers import create_timer
from core.helpers import format_remaining


def setup(bot: commands.Bot):
    @bot.command(name="timerdate")
    async def timerdate_cmd(
        ctx: commands.Context,
        date: str,
        time_str: str,
        gmt: str,
        *, text: str = ""
    ):
        """
        Format:
        !timerdate 31.12.2025 23:59 +3 New Year! --pin
        """
        # Pin flag
        should_pin = False
        if text.endswith("--pin"):
            should_pin = True
            text = text[:-5].strip()
        elif text.endswith("pin"):
            should_pin = True
            text = text[:-3].strip()

        if not text:
            text = "⏰ Time is up!"

        # Parse date
        try:
            base_dt = datetime.strptime(f"{date} {time_str}", "%d.%m.%Y %H:%M")

            if not (gmt.startswith("+") or gmt.startswith("-")):
                return await ctx.send("❌ GMT must be in format +3 / -5")

            tz_offset = int(gmt)
            tz = timezone(timedelta(hours=tz_offset))
            target_dt = base_dt.replace(tzinfo=tz)

            now = datetime.now(tz)
            remaining = int((target_dt - now).total_seconds())
            if remaining <= 0:
                return await ctx.send("❌ This date has already passed in the specified GMT.")
        except Exception:
            return await ctx.send(
                "❌ Invalid format.\n"
                "Example:\n"
                "`!timerdate 31.12.2025 23:59 +3 New Year! --pin`"
            )

        embed = discord.Embed(
            title=f"⏳ Timer: {text}",
            description=(
                f"Date: **{date} {time_str} (GMT{gmt})**\n"
                f"Remaining: **{format_remaining(remaining)}**"
            ),
            color=discord.Color.orange(),
        )

        msg = await ctx.send(embed=embed)

        # Pin
        if should_pin:
            try:
                await msg.pin()
            except discord.Forbidden:
                await ctx.send("⚠️ I don't have permission to pin messages.")
            except Exception as e:
                await ctx.send(f"⚠️ Pin error: {e}")

        timer_id = create_timer(
            channel_id=ctx.channel.id,
            message_id=msg.id,
            text=text,
            timestamp=int(target_dt.timestamp()),
            tz_offset=tz_offset,
            pinned=should_pin,
        )

        await ctx.send(f"✅ Timer created! ID: **{timer_id}**")
