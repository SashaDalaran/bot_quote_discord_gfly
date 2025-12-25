import os
import logging
import discord
from discord.ext import commands

# ===========================
# Logging Configuration
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("bot")

# ===========================
# Environment Variables
# ===========================
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("❌ Missing environment variable: DISCORD_BOT_TOKEN")

# ===========================
# Import Daily Task Modules
# (imported after env check)
# ===========================

from daily.banlu.banlu_daily import (
    send_banlu_daily,
    send_banlu_once,
)

from daily.holidays.holidays_daily import (
    send_holidays_daily,
    send_once_if_missed_holidays,
)

from daily.birthday.birthday_daily import (
    send_birthday_daily,
    send_once_if_missed_birthday,
)

# ===========================
# Bot Initialization
# ===========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
)


# ===========================
# Dependency Injection
# Attach bot reference into task modules
# ===========================
for task in (
    send_banlu_daily,
    send_banlu_once,
    send_holidays_daily,
    send_once_if_missed_holidays,
    send_birthday_daily,
    send_once_if_missed_birthday,
):
    task.bot = bot


# ===========================
# Command Loader
# ===========================
def load_all_commands() -> None:
    """
    Imports and registers all command Cogs.
    Structured this way to avoid circular imports and
    allow clear entrypoint logic.
    """
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

    logger.info("All command modules loaded successfully.")


# ===========================
# Bot Lifecycle Events
# ===========================
@bot.event
async def on_ready():
    logger.info("✅ Bot is online.")
    logger.info(f"Logged in as: {bot.user} (ID: {bot.user.id})")

    # Start background tasks if not already running
    if not send_banlu_daily.is_running():
        send_banlu_daily.start()
        logger.info("Started task: send_banlu_daily")

    if not send_holidays_daily.is_running():
        send_holidays_daily.start()
        logger.info("Started task: send_holidays_daily")


    if not send_birthday_daily.is_running():
        send_birthday_daily.start()
        logger.info("Started task: send_birthday_daily")

    # Run fallback/missed checks
    logger.info("Running missed-task fallback checks...")
    await send_banlu_once()
    await send_once_if_missed_holidays()
    await send_once_if_missed_birthday()

    logger.info("Background scheduler initialized successfully.")


# ===========================
# Entrypoint
# ===========================
def main():
    """Main application entrypoint."""
    load_all_commands()
    logger.info("Launching bot...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
