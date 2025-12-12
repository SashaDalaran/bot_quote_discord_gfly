import logging
import os

import discord
from discord.ext import commands

from core.timer_engine import update_timers_loop
from daily.banlu.banlu_daily import send_banlu_daily, send_once_if_missed
from daily.holidays.holidays_daily import (
    send_holidays_daily,
    send_once_if_missed_holidays
)

# ===========================
# Logging
# ===========================
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("bot")

# ===========================
# Environment
# ===========================
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ===========================
# Bot Setup
# ===========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ===========================
# Load Commands
# ===========================
def load_all_commands():
    from commands.quotes import setup as setup_quotes
    from commands.murloc_ai import setup as setup_murloc
    from commands.simple_timer import setup as setup_simple_timer
    from commands.date_timer import setup as setup_date_timer
    from commands.cancel import setup as setup_cancel
    from commands.help_cmd import setup as setup_help
    from commands.holidays_cmd import setup as setup_holidays

    setup_quotes(bot)
    setup_murloc(bot)
    setup_simple_timer(bot)
    setup_date_timer(bot)
    setup_cancel(bot)
    setup_help(bot)
    setup_holidays(bot)


load_all_commands()

# ===========================
# Bot Ready Event
# ===========================
@bot.event
async def on_ready():
    logger.info("Bot online and ready.")

    # Attach bot instance to all daily tasks
    send_banlu_daily.bot = bot
    send_holidays_daily.bot = bot
    send_once_if_missed.bot = bot
    send_once_if_missed_holidays.bot = bot
    update_timers_loop.bot = bot

    # Start BAN'LU daily loop
    if not send_banlu_daily.is_running():
        send_banlu_daily.start()

    # Start Holidays daily loop
    if not send_holidays_daily.is_running():
        send_holidays_daily.start()

    # Run missed BAN'LU once on startup
    await send_once_if_missed()

    # Run missed Holidays once on startup
    await send_once_if_missed_holidays()

    # Start reminders/timers engine
    if not update_timers_loop.is_running():
        update_timers_loop.start()

    logger.info("All background tasks started successfully.")

# ===========================
# Entry Point
# ===========================
def main():
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN is missing.")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
