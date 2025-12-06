# commands/cancel.py
from datetime import datetime, timedelta, timezone

from discord.ext import commands

from core.timers import date_timers, delete_timer, save as save_timers
from core.helpers import format_remaining


def setup(bot: commands.Bot):
    @bot.command(name="cancel")
    async def cmd_cancel(ctx: commands.Context, timer_id: int):
        """Cancel a timer by its ID."""
        if timer_id not in date_timers:
            return await ctx.send("❌ No timer found with this ID.")

        delete_timer(timer_id)
        await ctx.send(f"🛑 Timer {timer_id} has been canceled.")

    @bot.command(name="cancelall")
    async def cmd_cancel_all(ctx: commands.Context):
        """Cancel all timers in this channel."""
        removed = []

        for tid, t in list(date_timers.items()):
            if t["channel_id"] == ctx.channel.id:
                removed.append(tid)
                delete_timer(tid)

        if not removed:
            return await ctx.send("🔕 There are no active timers in this channel.")

        await ctx.send(f"🛑 Removed timers: **{len(removed)}**")

    @bot.command(name="timers")
    async def cmd_list_timers(ctx: commands.Context):
        """List all active timers in this channel."""
        timers_here = [t for t in date_timers.values() if t["channel_id"] == ctx.channel.id]

        if not timers_here:
            return await ctx.send("🔔 No timers set in this channel.")

        text = "📌 **Active Timers:**\n\n"
        for t in timers_here:
            tz = timezone(timedelta(hours=t["tz_offset"]))
            dt = datetime.fromtimestamp(t["target_timestamp"], tz)
            text += (
                f"• ID **{t['timer_id']}** — {t['text']}\n"
                f"  Date: **{dt.strftime('%d.%m.%Y %H:%M')} (GMT{t['tz_offset']:+})**\n\n"
            )

        await ctx.send(text)
