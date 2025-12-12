# ==================================================
# commands/simple_timer.py — Simple Countdown Timer
# ==================================================

import asyncio
import discord
from discord.ext import commands


# ===========================
# Setup Function
# Registers: !timer
# ===========================
def setup(bot: commands.Bot) -> None:

    # -------------------------------------------
    # !timer <duration> <text>
    #
    # Examples:
    # !timer 10s Hello!
    # !timer 5m Break time!
    # !timer 1h20m Boss pull!
    #
    # Default message: "⏰ Time's up!"
    # -------------------------------------------
    @bot.command(name="timer")
    async def timer_cmd(
        ctx: commands.Context,
        duration: str,
        *,
        text: str = "⏰ Time's up!"
    ):
        """Create a simple countdown timer."""

        # ===========================
        # Parse Duration
        # ===========================
        try:
            total_seconds = parse_duration(duration)
        except Exception as e:
            return await ctx.send(f"❌ Error: {e}")

        # ===========================
        # Send "Timer Started" Embed
        # ===========================
        embed = discord.Embed(
            title="⏱ Timer started!",
            description=(
                f"{ctx.author.mention}\n"
                f"Duration: **{total_seconds} sec**\n"
                f"Message: {text}"
            ),
            color=discord.Color.orange(),
        )
        await ctx.send(embed=embed)

        # ===========================
        # Wait for Timer
        # ===========================
        await asyncio.sleep(total_seconds)

        # ===========================
        # Send "Timer Finished" Embed
        # ===========================
        embed_done = discord.Embed(
            title="⏰ Timer finished!",
            description=f"{ctx.author.mention}\n{text}",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed_done)


# ===========================
# Duration Parser
# Allowed formats:
#   10s / 5m / 2h / 1h20m / 90
# ===========================
def parse_duration(text: str) -> int:
    """
    Parse a smart duration format into seconds.

    Rules:
    - If it's just a number: treated as minutes (e.g., "90" → 5400 sec)
    - Supports mixed units: 1h20m, 2h5m30s, etc.
    - Units: h / m / s
    """
    text = text.strip().lower()

    # -------------------------------------------
    # Pure number => treat as minutes
    # -------------------------------------------
    if text.isdigit():
        return int(text) * 60

    total = 0
    num = ""

    # -------------------------------------------
    # Convert one segment (e.g., "10m")
    # -------------------------------------------
    def flush(unit: str, val: str) -> int:
        if not val:
            raise ValueError("Missing number before unit")

        v = int(val)

        if unit == "h":
            return v * 3600
        if unit == "m":
            return v * 60
        if unit == "s":
            return v

        raise ValueError("Unknown unit")

    # -------------------------------------------
    # Parse character-by-character
    # -------------------------------------------
    for ch in text:
        if ch.isdigit():
            num += ch
        elif ch in "hms":
            total += flush(ch, num)
            num = ""
        else:
            raise ValueError(f"Unexpected character: {ch}")

    # If any remainder exists, treat as minutes
    if num:
        total += int(num) * 60

    return total
