# ==================================================
# commands/date_timer.py — Date-Based Timer Command
# ==================================================

from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from core.timers import create_timer
from core.helpers import format_remaining


# ===========================
# Setup Function
# Registers the !timerdate command
# ===========================
def setup(bot: commands.Bot) -> None:

    # ===========================
    # !timerdate DD.MM.YYYY HH:MM +TZ text --pin
    #
    # Example:
    # !timerdate 31.12.2025 23:59 +3 New Year! --pin
    # ===========================
    @bot.command(name="timerdate")
    async def timerdate_cmd(
        ctx: commands.Context,
        date: str,
        time_str: str,
        gmt: str,
        *, text: str = ""
    ):
        """Create a date-based timer with optional pinning."""

        # -------------------------------------------
        # Extract pin flag from text
        # -------------------------------------------
        should_pin = False
        raw_text = text.strip()

        if raw_text.endswith("--pin"):
            should_pin = True
            raw_text = raw_text[:-5].strip()

        elif raw_text.endswith("pin"):
            # user-friendly fallback: "pin" without dashes
            should_pin = True
            raw_text = raw_text[:-3].strip()

        if not raw_text:
            raw_text = "⏰ Time is up!"


        # ===========================
        # Parse: Date, Time, GMT Offset
        # ===========================
        try:
            # Parse DD.MM.YYYY and HH:MM
            base_dt = datetime.strptime(
                f"{date} {time_str}", "%d.%m.%Y %H:%M"
            )

            # Validate GMT format (+3 / -5)
            if not (gmt.startswith("+") or gmt.startswith("-")):
                return await ctx.send("❌ GMT must be in the format `+3` or `-5`.")

            tz_offset = int(gmt)
            tz = timezone(timedelta(hours=tz_offset))

            target_dt = base_dt.replace(tzinfo=tz)
            now = datetime.now(tz)
            remaining_seconds = int((target_dt - now).total_seconds())

            if remaining_seconds <= 0:
                return await ctx.send(
                    "❌ This date has already passed in the specified GMT."
                )

        except Exception:
            return await ctx.send(
                "❌ Invalid format.\n"
                "Example:\n"
                "`!timerdate 31.12.2025 23:59 +3 New Year! --pin`"
            )


        # ===========================
        # Create Preview Embed
        # ===========================
        embed = discord.Embed(
            title=f"⏳ Timer: {raw_text}",
            description=(
                f"Date: **{date} {time_str} (GMT{gmt})**\n"
                f"Remaining: **{format_remaining(remaining_seconds)}**"
            ),
            color=discord.Color.orange(),
        )

        msg = await ctx.send(embed=embed)


        # ===========================
        # Pin Message (Optional)
        # ===========================
        if should_pin:
            try:
                await msg.pin()
            except discord.Forbidden:
                await ctx.send("⚠️ I don't have permission to pin messages.")
            except Exception as e:
                await ctx.send(f"⚠️ Pin error: {e}")


        # ===========================
        # Save Timer in Database
        # ===========================
        timer_id = create_timer(
            channel_id=ctx.channel.id,
            message_id=msg.id,
            text=raw_text,
            timestamp=int(target_dt.timestamp()),
            tz_offset=tz_offset,
            pinned=should_pin,
        )

        await ctx.send(f"✅ Timer created! ID: **{timer_id}**")
