<p align="center">
  <img src="Murloc-Fulltime-Logo.gif" width="220" alt="Murloc Bot Logo" />
</p>

<h1 align="center">bot_quote_discord_gfly</h1>

<p align="center">
  A production-ready Discord bot built with <b>Python 3.11</b> and <b>discord.py 2.4.0</b>.<br/>
  Clean layered architecture (Commands → Services → Core) + scheduled daily posts via <b>discord.ext.tasks</b>.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/discord.py-2.4.0-7289DA?style=for-the-badge&logo=discord" />
  <img src="https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/Fly.io-Machines-8A2BE2?style=for-the-badge" />
</p>

---

## ✨ Overview

**bot_quote_discord_gfly** is a modular Discord bot that combines:

- 💬 **Random Quotes** — random game quotes from datasets + a **“More”** button (no chat spam)
- 🐸 **Murloc AI** — a “wisdom generator” built from datasets + a **“More”** button
- ⏱ **Timers**
  - `!timer` — simple countdown (fire-and-forget)
  - `!timerdate` — persistent date/time countdown with **live message updates** + optional pin
  - `!timers / !cancel / !cancelall` — manage persistent timers
- 🎉 **Holidays System**
  - static holidays from JSON packs in `data/holidays/`
  - dynamic holidays via rules in `core/dynamic_holidays.py`
  - emoji/flags mapping in `core/holidays_flags.py` (and compatible mapping in `services/holidays_flags.py`)
- 📡 **Daily automated posts**
  - Ban’Lu / Naughty Dog daily quote + Steam screenshot
  - Holidays broadcast
  - Birthdays / Guild Events broadcast

This project is intentionally structured as a **reference-quality architecture** bot:
clean layers, predictable behavior, easy extensibility, and production-friendly deployment.

---

## 📌 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Commands](#-commands)
  - [Help](#help)
  - [Quotes](#quotes)
  - [Murloc AI](#murloc-ai)
  - [Timers](#timers)
  - [Holidays](#holidays)
- [Daily Jobs](#-daily-jobs)
- [Datasets & Content](#-datasets--content)
- [Environment Variables](#-environment-variables)
- [How to get Discord channel IDs](#-how-to-get-discord-channel-ids)
- [Deployment (Fly.io)](#-deployment-flyio)
- [Logging & Security Notes](#-logging--security-notes)
- [Troubleshooting](#-troubleshooting)
- [Known Limitations](#-known-limitations)
- [Roadmap (safe improvements)](#-roadmap-safe-improvements)

---

## 🚀 Features

### ✅ Commands / user features

- 💬 **Random Quotes** — `!quote`
  - sends an embed with the quote
  - includes a **More** button to fetch the next quote without retyping
- 🐸 **Murloc AI** — `!murloc_ai`
  - generates phrases from 3 datasets
  - includes a **More** button to roll again
- ⏱ **Countdown Timers**
  - `!timer` — relative countdown (`10s`, `5m`, `1h`, `1h20m`, or a plain number)
  - `!timerdate` — absolute date/time countdown with a timezone offset token (`+3`, `-5`) and optional `--pin`
  - persistent timers update a single message (edit), no chat spam
- 🎉 **Holiday System** — `!holidays`
  - merges static JSON packs and dynamic rules
  - shows flags/categories via emoji mapping

### ✅ Production / deployment

- 🐳 Docker multi-stage build
- Fly.io Machines ready (`fly.toml`)
- pinned dependencies (`requirements.txt`) for stability

---

## 🧠 Architecture

The bot follows a strict layered architecture:

```
Commands → Services → Core
```

### Commands (`commands/`)
User-facing Discord command handlers (`discord.ext.commands`):
- parse input and flags
- call the domain services / core
- send/edit messages, build UI components (Views / Buttons)

### Services (`services/`)
Domain layer helpers:
- data loading services (quotes / banlu / birthday)
- formatting helpers (birthday/guild events)
- parsing helpers (channel IDs from env)

### Core (`core/`)
Core engine + infrastructure:
- persistent timer store (`timers.json`)
- real-time timer update loop (`core/timer_engine.py`)
- shared helpers (formatting, update intervals)
- holiday rules + emoji mapping

### Daily jobs (`daily/`)
Cron-like scheduled tasks wired via `discord.ext.tasks.loop(time=...)`.

---

## 📁 Project Structure

> This is the **actual** folder layout in the repo.

```
bot_quote_discord_gfly/
│
├── bot.py                        # application entrypoint
│
├── commands/                     # Discord commands (user-facing layer)
│   ├── __init__.py
│   ├── cancel.py                 # !timers / !cancel / !cancelall (persistent timers)
│   ├── date_timer.py             # !timerdate (persistent + live updates + optional pin)
│   ├── help_cmd.py               # !help
│   ├── holidays_cmd.py           # !holidays
│   ├── murloc_ai.py              # !murloc_ai (+ "More" button)
│   ├── quotes.py                 # !quote (+ "More" button)
│   └── simple_timer.py           # !timer (simple countdown)
│
├── services/                     # service layer
│   ├── __init__.py
│   ├── banlu_service.py          # Ban'Lu / Naughty Dog quote dataset helpers
│   ├── birthday_format.py        # formatting guild events for Discord messages
│   ├── birthday_service.py       # birthday & guild events dataset helpers
│   ├── channel_ids.py            # parse comma-separated channel IDs from env
│   ├── holidays_flags.py         # emoji/flag/category mapping (compatible layer)
│   └── holidays_service.py       # merge static + dynamic holidays
│
├── core/                         # core logic (timers, models, helpers)
│   ├── __init__.py
│   ├── dynamic_holidays.py       # dynamic holiday rules (e.g., Easter)
│   ├── helpers.py                # file utils, timer storage, formatting, update intervals
│   ├── holidays_flags.py         # emoji mapping (COUNTRY_FLAGS, CATEGORY_EMOJIS)
│   ├── settings.py               # env + constants (token, feature flags, channels)
│   ├── timer_engine.py           # real-time timer update loop (edits timer embeds)
│   └── timers.py                 # persistent timer storage helpers (timers.json)
│
├── daily/                        # scheduled jobs (discord.ext.tasks)
│   ├── __init__.py
│   ├── banlu/
│   │   ├── __init__.py
│   │   └── banlu_daily.py        # daily quote + Steam screenshot (10:00 in BOT_TZ)
│   ├── holidays/
│   │   ├── __init__.py
│   │   └── holidays_daily.py     # holidays broadcast (10:01 in BOT_TZ)
│   └── birthday/
│       ├── __init__.py
│       └── birthday_daily.py     # birthdays/guild events (see note in Daily Jobs)
│
├── data/                        # Content & datasets
│   ├── holidays/                  # holiday JSON packs
│   │   └── December.json
│   │   └── January.json
|   |   └── February.json
│   ├── __init__.py             # package marker
│   ├── birthday.json           # guild events dataset
│   ├── murloc_endings.txt      # Murloc AI dataset
│   ├── murloc_middles.txt      # Murloc AI dataset
│   ├── murloc_starts.txt       # Murloc AI dataset
│   ├── quotersbanlu.txt        # Ban'Lu quotes dataset
│   └── quotes.txt              # quotes dataset
│
├── timers.json                   # persistent store (created at runtime, safe to commit-ignore)
│
├── Dockerfile
├── fly.toml
├── requirements.txt
├── Murloc-Fulltime-Logo.gif
└── README.md
```

---

## ⚡ Quick Start

### 1) Install deps (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Set environment variables

```bash
export DISCORD_BOT_TOKEN="xxx"

# optional channels (one or many, comma-separated):
export BANLU_CHANNEL_ID="123456789012345678"
export HOLIDAYS_CHANNEL_ID="111111111111111111,222222222222222222"
export BIRTHDAY_CHANNEL_ID="333333333333333333"

# scheduling timezone for daily jobs (default: Europe/Moscow)
export BOT_TZ="Europe/Moscow"
```

### 3) Run bot

```bash
python bot.py
```

Bot uses prefix commands (default prefix is `!`).

---

## 🎮 Commands

### Help

```text
!help
```

Shows an embed-based command list.

---

### Quotes

```text
!quote
```

- pulls a random entry from `data/quotes.txt`
- renders a quote embed
- provides a **More** button to fetch another quote

> Dataset format: `Quote text — Source` (source becomes embed footer)

---

### Murloc AI

```text
!murloc_ai
```

Generates a phrase by combining random fragments from:

- `data/murloc_starts.txt`
- `data/murloc_middles.txt`
- `data/murloc_endings.txt`

Also includes a **More** button.

---

## Timers

### `!timer` — simple countdown

**Format**
```text
!timer <duration> [message...]
```

**Supported duration formats**
- `10s`, `5m`, `2h`, `1h20m`
- plain number → treated as **minutes** (e.g., `90` means 90 minutes)

**Examples**
```text
!timer 10s Tea
!timer 5m
!timer 1h30m Raid
!timer 90 Long break
```

> `!timer` is a simple sleep-based countdown. It does not persist and cannot be cancelled.

---

### `!timerdate` — persistent date/time countdown (GMT + optional pin)

**Format**
```text
!timerdate DD.MM.YYYY HH:MM +TZ [text...] [--pin]
```

**Examples**
```text
!timerdate 31.12.2025 23:59 +3 New Year! --pin
!timerdate 05.01.2026 19:30 -5 Meeting
```

Behavior:
- creates a timer embed message
- optionally pins that message (`--pin` or `pin`)
- stores timer in `timers.json`
- updates the embed in real-time via `core/timer_engine.py`

**Manage persistent timers**
```text
!timers
!cancel <ID>
!cancelall
```

---

## Holidays

### `!holidays`

```text
!holidays
```

Shows upcoming holidays:
- loads static packs from `data/holidays/*.json`
- merges dynamic holidays from `core/dynamic_holidays.py`
- uses emoji mapping from `core/holidays_flags.py`

---

## 🔁 Daily Jobs

Daily jobs are scheduled via `discord.ext.tasks.loop(time=...)` and use `BOT_TZ` (default: `Europe/Moscow`).

| Job | Module | Scheduled time in BOT_TZ | Env var |
|---|---|---:|---|
| Ban’Lu / Naughty Dog daily | `daily/banlu/banlu_daily.py` | 10:00 | `BANLU_CHANNEL_ID` (also supports `BANLU_CHANNEL_IDS`) |
| Holidays broadcast | `daily/holidays/holidays_daily.py` | 10:01 | `HOLIDAYS_CHANNEL_ID` |
| Birthday / Guild events | `daily/birthday/birthday_daily.py` | **see note below** | `BIRTHDAY_CHANNEL_ID` |

**Important note (current code behavior):**  
`daily/birthday/birthday_daily.py` has a schedule mismatch: it loops at **10:02** in `BOT_TZ`, but its “recovery / missed-run” logic checks **10:05**. If you want a single canonical time, make those values identical in that file.

**Catch-up behavior:**  
Each daily module includes a “run-on-start” safety check (best effort), so a restart near the scheduled time doesn’t silently skip the daily post.

---

## 📦 Datasets & Content

### Quotes
- `data/quotes.txt` — one quote per line  
  recommended format: `Quote — Source`

### Ban’Lu / Naughty Dog
- `data/quotersbanlu.txt` — dataset for the daily post

### Murloc AI
- `data/murloc_starts.txt`
- `data/murloc_middles.txt`
- `data/murloc_endings.txt`

### Holidays
- `data/holidays/*.json` — static holiday packs  
- `core/dynamic_holidays.py` — dynamic holiday rules

### Birthdays / Guild Events
- `data/birthday.json` — dataset used by the birthday daily job

---

## 🔐 Environment Variables

### Required

| Variable | Description |
|---|---|
| `DISCORD_BOT_TOKEN` | Discord bot token |

### Optional

| Variable | Description |
|---|---|
| `BANLU_CHANNEL_ID` / `BANLU_CHANNEL_IDS` | channel(s) for Ban’Lu daily |
| `HOLIDAYS_CHANNEL_ID` | channel(s) for Holidays daily |
| `BIRTHDAY_CHANNEL_ID` | channel(s) for Birthday/Guild Events daily |
| `BOT_TZ` | scheduling timezone for daily jobs (default `Europe/Moscow`) |

**Multi-channel example**
```bash
fly secrets set HOLIDAYS_CHANNEL_ID="111111111111111111,222222222222222222"
```

---

## 🆔 How to get Discord channel IDs

1. Discord → **User Settings** → **Advanced** → enable **Developer Mode**
2. Right click the channel → **Copy Channel ID**
3. Paste into `BANLU_CHANNEL_ID` / `HOLIDAYS_CHANNEL_ID` / `BIRTHDAY_CHANNEL_ID`

---

## 🐳 Deployment (Fly.io)

### Deploy
```bash
fly deploy
fly logs
```

### Set secrets
```bash
fly secrets set DISCORD_BOT_TOKEN="xxx"
fly secrets set BANLU_CHANNEL_ID="123..."
fly secrets set HOLIDAYS_CHANNEL_ID="111,222"
fly secrets set BIRTHDAY_CHANNEL_ID="333"
fly secrets set BOT_TZ="Europe/Moscow"
```

---

## 🧯 Logging & Security Notes

### Token safety
- Never commit `.env` with tokens.
- Use Fly secrets (`fly secrets set ...`).
- Keep log level sane (`INFO` is ok, avoid verbose HTTP dumps).

### If token was exposed
- regenerate token in Discord Developer Portal
- update `DISCORD_BOT_TOKEN` via `fly secrets set`

---

## 🛠 Troubleshooting

### Bot starts but commands don’t work
- verify `DISCORD_BOT_TOKEN`
- make sure the bot is invited to your server
- check required intents / permissions in Discord Developer Portal

### Timers don’t update / `!timerdate` embed stays static
- ensure the background loop `core/timer_engine.py` is started in `bot.py`
- confirm the bot can edit its own messages

### Pin errors for `--pin`
- pin requires channel permissions (`Manage Messages`) or admin rights

### Daily jobs don’t post
- verify channel IDs are correct
- ensure bot has permission to send messages in those channels
- check timezone config: `BOT_TZ`

---

## 🧩 Known Limitations

These notes match current implementation:

- `!timer` is fire-and-forget: no persistence, no cancel.
- `!timerdate` currently expects **DD.MM.YYYY** date format (not `YYYY-MM-DD`).
- Birthday daily job has a schedule mismatch (10:02 loop vs 10:05 recovery check) — see [Daily Jobs](#-daily-jobs).

---

## 🗺 Roadmap (safe improvements)

Safe improvements = minimal risk, no refactor avalanche:

- [ ] Unify birthday schedule time (make loop time == recovery check)
- [ ] Add `!channel_id` utility command (Discord equivalent of Telegram `/chat_id`)
- [ ] Add a small “smoke check” script:
  - imports modules
  - validates env vars
  - validates dataset files exist
- [ ] Add a quick “permissions checklist” section to the `!help` embed

---

<p align="center">
  <b>Murloc Edition 🐸 — Mrrglglglgl</b>
</p>
