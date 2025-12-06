import logging
import os

import discord
from discord.ext import commands

from core.timer_engine import update_timers_loop
from daily.banlu.banlu_daily import send_banlu_daily, send_once_if_missed

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("bot")

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# передаём бота в daily task
send_banlu_daily.bot = bot
update_timers_loop.bot = bot


def load_all_commands():
    from commands.quotes import setup as setup_quotes
    from commands.murloc_ai import setup as setup_murloc
    from commands.simple_timer import setup as setup_simple_timer
    from commands.date_timer import setup as setup_date_timer
    from commands.cancel import setup as setup_cancel
    from commands.help_cmd import setup as setup_help
    from commands.holydays_cmd import setup as setup_holydays

    setup_quotes(bot)
    setup_murloc(bot)
    setup_simple_timer(bot)
    setup_date_timer(bot)
    setup_cancel(bot)
    setup_help(bot)
    setup_holydays(bot)


load_all_commands()


@bot.event
async def on_ready():
    logger.info("Bot started!")

    if not send_banlu_daily.is_running():
        send_banlu_daily.start()

    await send_once_if_missed(bot)

    if not update_timers_loop.is_running():
        update_timers_loop.start()

    logger.info("Background tasks started.")


def main():
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN missing")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
