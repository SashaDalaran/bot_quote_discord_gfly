# ==================================================
# daily/birthday/birthday_daily.py — Daily Birthday / Challenge Sender
# ==================================================

import os
import json
import logging
from datetime import datetime, timedelta, timezone, time, date

import discord
from discord.ext import tasks

from core.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

logger = logging.getLogger("birthday_daily")

# ===========================
# Configuration
# ===========================
TZ = timezone(timedelta(hours=3))  # GMT+3

BIRTHDAY_CHANNEL_IDS = [
    cid.strip()
    for cid in os.getenv("BIRTHDAY_CHANNEL_IDS", "").split(",")
    if cid.strip().isdigit()
]

BIRTHDAY_DATA_PATH = os.getenv(
    "BIRTHDAY_DATA_PATH",
    "data/birthday.json",
)

# ===========================
# Helpers — Date logic
# ===========================
def is_today_in_date(date_str: str, today: date) -> bool:
    """
    Supports:
    - MM-DD
    - MM-DD:MM-DD (including year wrap)
    """
    if ":" not in date_str:
        m, d = map(int, date_str.split("-"))
        return today.month == m and today.day == d

    start_str, end_str = date_str.split(":")
    sm, sd = map(int, start_str.split("-"))
    em, ed = map(int, end_str.split("-"))

    start = date(today.year, sm, sd)
    end = date(today.year, em, ed)

    # wrap through New Year
    if end < start:
        return today >= start or today <= end

    return start <= today <= end


# ===========================
# Data loading
# ===========================
def load_birthdays() -> list[dict]:
    try:
        with open(BIRTHDAY_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception(f"Failed to load birthday data: {e}")
        return []


def filter_events(events: list[dict], category: str, today: date) -> list[dict]:
    return [
        e for e in events
        if category in e.get("category", [])
        and is_today_in_date(e.get("date", ""), today)
    ]


# ===========================
# Message formatters
# ===========================
def format_challenge_message() -> str:
    emoji = CATEGORY_EMOJIS.get("Сhallenge", "🔥")
    return f"{emoji} **ЧЕЛЕНДЖ МУРЛОКОВ В АКТИВЕ!**"


def format_hero_message(event: dict) -> str:
    emoji = CATEGORY_EMOJIS.get("Accept", "🏆")
    country = event.get("countries", [""])[0]
    flag = COUNTRY_FLAGS.get(country, "🏆")
    return f"{emoji} {flag} **ГЕРОЙ МУРЛОКОВ:** {event['name']}"


def format_birthday_message(events: list[dict]) -> str:
    emoji = CATEGORY_EMOJIS.get("Birthday", "🎂")
    names = ", ".join(e["name"] for e in events)
    return f"{emoji} **ДНИ РОЖДЕНИЯ МУРЛОКОВ СЕГОДНЯ:**\n{names}"


# ==================================================
# Daily Scheduled Task — 10:05 GMT+3
# ==================================================
@tasks.loop(time=time(hour=10, minute=5, tzinfo=TZ))
async def send_birthday_daily():
    bot = send_birthday_daily.bot
    logger.info("Running birthday daily task...")

    today = datetime.now(TZ).date()
    events = load_birthdays()

    challenges =s = filter_events(events, "Сhallenge", today)
    heroes = filter_events(events, "Accept", today)
    birthdays = filter_events(events, "Birthday", today)

    messages: list[str] = []

    if challenges:
        messages.append(format_challenge_message())

    for hero in heroes:
        messages.append(format_hero_message(hero))

    if birthdays:
        messages.append(format_birthday_message(birthdays))

    if not messages:
        logger.info("No birthday / challenge events today.")
        return

    for channel_id in BIRTHDAY_CHANNEL_IDS:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            logger.warning(f"Channel {channel_id} not found.")
            continue

        for msg in messages:
            try:
                await channel.send(msg)
            except Exception as e:
                logger.exception(f"Failed to send birthday message: {e}")


# ==================================================
# One-Time Recovery (Bot Restart After 10:05)
# ==================================================
async def send_once_if_missed_birthday():
    bot = send_once_if_missed_birthday.bot

    now = datetime.now(TZ)
    scheduled = now.replace(hour=10, minute=5, second=0, microsecond=0)

    if now <= scheduled:
        return

    today = now.date()
    events = load_birthdays()

    challenges = filter_events(events, "Сhallenge", today)
    heroes = filter_events(events, "Accept", today)
    birthdays = filter_events(events, "Birthday", today)

    messages: list[str] = []

    if challenges:
        messages.append(format_challenge_message())

    for hero in heroes:
        messages.append(format_hero_message(hero))

    if birthdays:
        messages.append(format_birthday_message(birthdays))

    if not messages:
        return

    logger.info("Bot restarted after schedule → sending birthday messages once")

    for channel_id in BIRTHDAY_CHANNEL_IDS:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            continue

        for msg in messages:
            try:
                await channel.send(msg)
            except Exception:
                logger.exception("Failed to send missed birthday message")
