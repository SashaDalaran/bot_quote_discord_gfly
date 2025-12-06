# commands/simple_timer.py
import asyncio
import discord
from discord.ext import commands


def setup(bot: commands.Bot):
    @bot.command(name="timer")
    async def timer_cmd(ctx: commands.Context, duration: str, *, text="⏰ Time's up!"):
        try:
            total_sec = parse_duration(duration)
        except Exception as e:
            return await ctx.send(f"❌ Error: {e}")

        embed = discord.Embed(
            title="⏱ Timer started!",
            description=(
                f"{ctx.author.mention}\n"
                f"Duration: **{total_sec} sec**\n"
                f"Message: {text}"
            ),
            color=discord.Color.orange(),
        )
        await ctx.send(embed=embed)

        await asyncio.sleep(total_sec)

        embed2 = discord.Embed(
            title="⏰ Timer finished!",
            description=f"{ctx.author.mention}\n{text}",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed2)


def parse_duration(text: str) -> int:
    """
    Duration parser:
    10s / 5m / 2h / 1h20m / 90
    """
    text = text.strip().lower()
    if text.isdigit():
        return int(text) * 60

    total = 0
    num = ""

    def flush(unit, val):
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

    for ch in text:
        if ch.isdigit():
            num += ch
        elif ch in "hms":
            total += flush(ch, num)
            num = ""
        else:
            raise ValueError(f"Unexpected char: {ch}")

    if num:
        total += int(num) * 60

    return total
