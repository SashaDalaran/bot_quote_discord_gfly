# ==================================================
# commands/cancel.py — Timer Cancellation Commands
# ==================================================

from datetime import datetime, timedelta, timezone
from typing import List

from discord.ext import commands

from core.timers import date_timers, delete_timer, save as save_timers
from core.helpers import format_remaining


# ===========================
# Setup Function
# Registers all cancel-related commands
# ===========================
def setup(bot: commands.Bot) -> None:

    # ===========================
    # !cancel <id>
    # Cancel a specific timer by ID
    # ===========================
    @bot.command(name="cancel")
    async def cmd_cancel(ctx: commands.Context, timer_id: int):
        """Cancel a timer by its ID."""

        timer = date_timers.get(timer_id)
        if timer is None:
            return await ctx.send("❌ No timer found with this ID.")

        delete_timer(timer_id)
        await ctx.send(f"🛑 Timer **{timer_id}** has been canceled.")

    # ===========================
    # !cancelall
    # Cancel all timers in the current channel
    # ===========================
    @bot.command(name="cancelall")
    async def cmd_cancel_all(ctx: commands.Context):
        """Cancel all timers in this channel."""

        channel_id = ctx.channel.id
        removed: List[int] = []

        # Iterate over a copy since we mutate the dict
        for tid, timer in list(date_timers.items()):
            if timer["channel_id"] == channel_id:
                removed.append(tid)
                delete_timer(tid)

        if not removed:
            return await ctx.send("🔕 There are no active timers in this channel.")

        await ctx.send(f"🛑 Removed **{len(removed)}** timer(s).")

    # ===========================
    # !timers
    # Display all active timers in the current channel
    # ===========================
    @bot.command(name="timers")
    async def cmd_list_timers(ctx: commands.Context):
        """List all active timers in this channel."""

        channel_id = ctx.channel.id
        timers_here = [t for t in date_timers.values() if t["channel_id"] == channel_id]

        if not timers_here:
            return await ctx.send("🔔 No timers set in this channel.")

        # Build output
        lines = ["📌 **Active Timers:**", ""]

        for t in timers_here:
            tz = timezone(timedelta(hours=t["tz_offset"]))
            dt = datetime.fromtimestamp(t["target_timestamp"], tz)

            lines.append(
                f"• ID **{t['timer_id']}** — {t['text']}\n"
                f"  Date: **{dt.strftime('%d.%m.%Y %H:%M')} "
                f"(GMT{t['tz_offset']:+})**\n"
            )

        await ctx.send("\n".join(lines))
