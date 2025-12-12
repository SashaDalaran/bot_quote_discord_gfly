import os
import logging
from discord.ext import commands
import discord

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("bot")

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("❌ Environment variable DISCORD_BOT_TOKEN is missing!")

# === Daily Tasks ===
from daily.banlu.banlu_daily import (
    send_banlu_daily,
    send_once_if_missed as send_banlu_once,
)

from daily.holidays.holidays_daily import (
    send_holidays_daily,
    send_once_if_missed_holidays,
)


# === Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# === Attach bot reference to tasks ===
send_banlu_daily.bot = bot
send_banlu_once.bot = bot

send_holidays_daily.bot = bot
send_once_if_missed_holidays.bot = bot


# === Load Commands ===
def load_all_commands():
    from commands.quotes import setup as setup_quotes
    from commands.murloc_ai import setup as setup_ai
    from commands.simple_timer import setup as setup_simple_timer
    from commands.date_timer import setup as setup_date_timer
    from commands.cancel import setup as setup_cancel
    from commands.help_cmd import setup as setup_help
    from commands.holidays_cmd import setup as setup_holidays

    setup_quotes(bot)
    setup_ai(bot)
    setup_simple_timer(bot)
    setup_date_timer(bot)
    setup_cancel(bot)
    setup_help(bot)
    setup_holidays(bot)


@bot.event
async def on_ready():
    logger.info("✅ Bot online and ready.")
    logger.info(f"Logged in as: {bot.user} (ID: {bot.user.id})")

    # Start daily tasks if not running
    if not send_banlu_daily.is_running():
        send_banlu_daily.start()
        logger.info("Started: send_banlu_daily")

    if not send_holidays_daily.is_running():
        send_holidays_daily.start()
        logger.info("Started: send_holidays_daily")

    # Run missed messages detection
    logger.info("Running missed-task fallback checks...")
    await send_banlu_once()
    await send_once_if_missed_holidays()

    logger.info("All background tasks started successfully.")


# === Start Bot ===
if __name__ == "__main__":
    load_all_commands()
    logger.info("Starting bot...")
    bot.run(DISCORD_TOKEN)
