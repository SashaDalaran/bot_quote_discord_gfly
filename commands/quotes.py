# commands/quotes.py
import os
import random

import discord
from discord.ext import commands

from core.helpers import load_lines


QUOTES_FILE = os.getenv("QUOTES_FILE", "data/quotes.txt")


class QuoteView(discord.ui.View):
    def __init__(self, quotes: list[str]):
        super().__init__(timeout=None)
        self.quotes = quotes

    @discord.ui.button(label="More", style=discord.ButtonStyle.primary)
    async def more_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        phrase = random.choice(self.quotes)
        text, src = (phrase.split(" — ", 1) + ["Unknown"])[:2]

        embed = discord.Embed(
            title="🎮 GAME QUOTE",
            description=text,
            color=discord.Color.blue(),
        )
        embed.set_footer(text=src)

        await interaction.response.send_message(embed=embed, view=QuoteView(self.quotes))


def setup(bot: commands.Bot):
    quotes = load_lines(QUOTES_FILE)

    @bot.command(name="quote")
    async def quote_cmd(ctx: commands.Context):
        if not quotes:
            return await ctx.send("Quotes file is empty 😢")

        phrase = random.choice(quotes)
        text, src = (phrase.split(" — ", 1) + ["Unknown"])[:2]

        embed = discord.Embed(
            title="🎮 GAME QUOTE",
            description=text,
            color=discord.Color.blue(),
        )
        embed.set_footer(text=src)

        await ctx.send(embed=embed, view=QuoteView(quotes))
