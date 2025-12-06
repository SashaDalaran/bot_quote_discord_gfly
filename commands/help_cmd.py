# commands/help_cmd.py
import discord
from discord.ext import commands


def setup(bot: commands.Bot):
    @bot.command(name="help")
    async def cmd_help(ctx: commands.Context):
        embed = discord.Embed(
            title="📘 Just_Quotes Bot – Command List",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🎮 Quotes",
            value="**!quote** — Random game quote\n"
                  "**!murloc_ai** — Generate Murloc AI wisdom",
            inline=False
        )

        embed.add_field(
            name="⏱ Simple Timer",
            value="`!timer 10m text`\n"
                  "Supports: `10s`, `5m`, `1h`, `1h20m`\n"
                  "Example: `!timer 30s Time to fight!`",
            inline=False
        )

        embed.add_field(
            name="🎯 Date Timer (GMT + optional pin)",
            value="`!timerdate DD.MM.YYYY HH:MM +TZ text --pin`\n"
                  "Example:\n"
                  "`!timerdate 31.12.2025 23:59 +3 New Year! --pin`\n\n"
                  "Countdown format: days / hours / minutes / seconds.\n"
                  "`--pin` is optional.",
            inline=False
        )

        embed.add_field(
            name="🛑 Timer Management",
            value=(
                "`!timers` — list active timers\n"
                "`!cancel <ID>` — cancel one timer\n"
                "`!cancelall` — delete all timers in this channel"
            ),
            inline=False
        )

        embed.set_footer(text="Murloc Edition 🐸")

        await ctx.send(embed=embed)
