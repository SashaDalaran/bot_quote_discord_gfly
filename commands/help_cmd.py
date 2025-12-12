# ==================================================
# commands/help_cmd.py — Help / Command Overview
# ==================================================

import discord
from discord.ext import commands


# ===========================
# Setup Function
# Registers the !help command
# ===========================
def setup(bot: commands.Bot) -> None:

    # ===========================
    # !help
    # Display full command reference
    # ===========================
    @bot.command(name="help")
    async def cmd_help(ctx: commands.Context):
        """Send a nicely formatted help menu embed."""

        embed = discord.Embed(
            title="📘 Just_Quotes Bot – Command List",
            color=discord.Color.blurple(),
        )

        # ===========================
        # Quotes
        # ===========================
        embed.add_field(
            name="🎮 Quotes",
            value=(
                "**!quote** — Random game quote\n"
                "**!murloc_ai** — Generate Murloc AI wisdom"
            ),
            inline=False,
        )

        # ===========================
        # Simple Timer
        # ===========================
        embed.add_field(
            name="⏱ Simple Timer",
            value=(
                "`!timer 10m text`\n"
                "Supports: `10s`, `5m`, `1h`, `1h20m`\n"
                "Example: `!timer 30s Time to fight!`"
            ),
            inline=False,
        )

        # ===========================
        # Date Timer
        # ===========================
        embed.add_field(
            name="🎯 Date Timer (GMT + optional pin)",
            value=(
                "`!timerdate DD.MM.YYYY HH:MM +TZ text --pin`\n"
                "Example: `!timerdate 31.12.2025 23:59 +3 New Year! --pin`\n\n"
                "Countdown format: days / hours / minutes / seconds.\n"
                "`--pin` is optional."
            ),
            inline=False,
        )

        # ===========================
        # Holidays
        # ===========================
        embed.add_field(
            name="🎉 Holidays",
            value=(
                "`!holidays` — Shows the next upcoming holiday across all JSON files.\n"
                "Includes: world, country-specific, religious, and dynamic holidays."
            ),
            inline=False,
        )

        # ===========================
        # Timer Management
        # ===========================
        embed.add_field(
            name="🛑 Timer Management",
            value=(
                "`!timers` — List active timers\n"
                "`!cancel <ID>` — Cancel one timer\n"
                "`!cancelall` — Delete all timers in this channel"
            ),
            inline=False,
        )

        embed.set_footer(text="Murloc Edition 🐸")

        await ctx.send(embed=embed)
