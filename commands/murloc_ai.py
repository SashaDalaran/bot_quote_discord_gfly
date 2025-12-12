# ==================================================
# commands/murloc_ai.py — Murloc AI Wisdom Generator
# ==================================================

import os
import random
import discord
from discord.ext import commands

from core.helpers import load_lines


# ===========================
# Environment-Configurable File Paths
# ===========================
MURLOC_STARTS_FILE = os.getenv("MURLOC_STARTS_FILE", "data/murloc_starts.txt")
MURLOC_MIDDLES_FILE = os.getenv("MURLOC_MIDDLES_FILE", "data/murloc_middles.txt")
MURLOC_ENDINGS_FILE = os.getenv("MURLOC_ENDINGS_FILE", "data/murloc_endings.txt")


# ===========================
# Phrase Generator
# ===========================
def generate_murloc_phrase(starts, middles, ends) -> str:
    """Randomly generate a Murloc wisdom phrase."""
    if not (starts and middles and ends):
        return "❌ Murloc AI data is missing."

    a = random.choice(starts)
    b = random.choice(middles)
    c = random.choice(ends)

    return f"{a} — {b}, {c}"


# ===========================
# Interactive UI View (Button: More)
# ===========================
class MurlocView(discord.ui.View):
    """UI component allowing users to request more Murloc wisdom."""

    def __init__(self, starts, middles, ends):
        super().__init__(timeout=None)
        self.starts = starts
        self.middles = middles
        self.ends = ends

    @discord.ui.button(label="More", style=discord.ButtonStyle.primary)
    async def more_ai(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        """Generate and return another Murloc wisdom phrase."""
        phrase = generate_murloc_phrase(self.starts, self.middles, self.ends)

        embed = discord.Embed(
            title="🐸 Murloc AI Wisdom 🧠",
            description=phrase,
            color=discord.Color.blue(),
        )
        embed.set_footer(text="🐸 Mrrglglglgl! 🐸")

        await interaction.response.send_message(
            embed=embed,
            view=MurlocView(self.starts, self.middles, self.ends),
        )


# ===========================
# Setup Function
# Registers the !murloc_ai command
# ===========================
def setup(bot: commands.Bot) -> None:
    # Preload data files once at startup
    starts = load_lines(MURLOC_STARTS_FILE)
    middles = load_lines(MURLOC_MIDDLES_FILE)
    ends = load_lines(MURLOC_ENDINGS_FILE)

    # -------------------------------------------
    # !murloc_ai — Generate a wisdom phrase
    # -------------------------------------------
    @bot.command(name="murloc_ai")
    async def murloc_ai_cmd(ctx: commands.Context):
        """Generate and send Murloc wisdom."""

        phrase = generate_murloc_phrase(starts, middles, ends)

        embed = discord.Embed(
            title="🐸 Murloc AI Wisdom 🧠",
            description=phrase,
            color=discord.Color.blue(),
        )
        embed.set_footer(text="🐸 Mrrglglglgl! 🐸")

        await ctx.send(
            embed=embed,
            view=MurlocView(starts, middles, ends),
        )
