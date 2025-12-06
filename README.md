<p align="center">
  <img src="Murloc-Fulltime-Logo.gif" width="220" alt="Project Logo" />
</p>

<h1 align="center">bot-quote-discord</h1>

<p align="center">
  A lightweight, production-ready Discord bot built with <b>Python</b>, <b>discord.py</b>, and <b>Fly.io</b>.
  <br>
  Minimal footprint. Clean architecture. Zero maintenance.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/discord.py-2.4+-7289DA?style=for-the-badge&logo=discord" />
  <img src="https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/Fly.io-Machines-8A2BE2?style=for-the-badge" />
  <img src="https://img.shields.io/badge/GitHub%20Actions-AutoDeploy-2088FF?style=for-the-badge&logo=githubactions" />
</p>

---

## ✨ Features

* 🎮 **Game Quotes** — random quotes with source attribution  
* 🧠 **Murloc AI** — generates Murloc wisdom  
* 📅 **Holidays System** — static + dynamic holidays from all countries  
* 🎉 **Daily Holiday Broadcast** — auto-posting today's holidays to chosen channels  
* ⏱ **Timers** — simple timers and GMT date-timers  
* 📌 **Pin Support** — optional auto-pin for date timers  
* 🔁 **Daily Scheduler** — Ban’Lu quotes every morning  
* 🐳 **Optimized Docker Image** (~40 MB)  
* ☁️ **Fly.io Ready** — fully automated deploy  
* 🔐 **Secure Secret Handling**

---

## 📁 Project Structure

```
bot_quote_discord/
│
├── bot.py
├── Dockerfile
├── fly.toml
├── requirements.txt
│
├── core/
│     ├── holidays_flags.py     # Country + religion flags
│     ├── timer_engine.py
│     └── helpers.py
│
├── commands/
│     ├── quotes.py
│     ├── murloc_ai.py
│     ├── simple_timer.py
│     ├── date_timer.py
│     └── holidays_cmd.py       # Holiday lookup command
│
├── daily/
│     ├── banlu/
│     │     └── banlu_daily.py
│     └── holidays/
│           └── holidays_daily.py   # Daily holiday poster
│
├── data/
│     └── holidays/              # All JSON holiday files
│           ├── world.json
│           ├── usa.json
│           ├── eu.json
│           ├── georgia.json
│           └── ... etc
│
└── .github/workflows/
       └── fly-deploy.yml
```

---

## 🎮 Commands Overview

### Quotes
```
!quote          — random game quote  
!murloc_ai      — Murloc AI wisdom
```

### Simple Timer
```
!timer 10m text  
Supports: 10s, 5m, 1h, 1h20m, 90
```

### Date Timer
```
!timerdate DD.MM.YYYY HH:MM +TZ text --pin
Example:
!timerdate 31.12.2025 23:59 +3 New Year! --pin
```

### Timer Management
```
!timers         — list active timers  
!cancel <ID>    — cancel one timer  
!cancelall      — clear all timers in channel
```

---

## 🎉 Holidays System

### Command
```
!holidays — shows the closest upcoming holiday (from all JSON files)
```

### How it works
✔ Loads **all holidays** from `data/holidays/*.json`  
✔ Supports **static** (e.g. 01-05) and **dynamic** (Easter etc.) holidays  
✔ Automatically detects **flag** (country or religion)  
✔ Returns the **nearest** future holiday

### Example response
```
🎉 Next Holiday
🇺🇸 Independence Day
📅 Date: 07-04
```

---

## 🔁 Daily Holiday Broadcast

The bot automatically:

🕙 Posts every day at **10:01 GMT+3**  
📌 Sends all holidays matching **today's date**  
📡 Sends to all channels listed in env-variable:

```
HOLIDAYS_CHANNEL_IDS="123,456,789"
```

Fallback:  
If the bot was offline — sends once on startup.

---

## 🔐 Environment Variables

| Variable                  | Description                          |
|--------------------------|--------------------------------------|
| `DISCORD_BOT_TOKEN`      | Bot token                            |
| `BANLU_CHANNEL_ID`       | Ban’Lu quote channel                 |
| `HOLIDAYS_CHANNEL_IDS`   | Comma-separated list of target IDs   |

Set using Fly:

```sh
fly secrets set HOLIDAYS_CHANNEL_IDS="123,456,789"
```

---

## ☁️ Deployment (Fly.io)

```
fly deploy
fly logs
fly secrets set DISCORD_BOT_TOKEN=...
```

---

<p align="center">
  <b>Murloc Edition 🐸 Mrrglglglgl!</b>
</p>
