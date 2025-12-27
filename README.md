<p align="center">
  <img src="Murloc-Fulltime-Logo.gif" width="220" alt="Project Logo" />
</p>

<h1 align="center">bot-quote-discord</h1>

<p align="center">
  A production-grade Discord bot powered by <b>Python 3.11</b>, <b>discord.py</b>, and <b>Fly.io Machines</b>.  
  Built for reliability, clean architecture, fast deployment, and minimal resource usage.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/discord.py-2.4+-7289DA?style=for-the-badge&logo=discord" />
  <img src="https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/Fly.io-Machines-8A2BE2?style=for-the-badge" />
  <img src="https://img.shields.io/badge/CI/CD-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions" />
</p>

---

# ✨ Overview!

`bot-quote-discord` is a lightweight Discord bot featuring:

- 🎮 **Random Game Quotes**  
- 🧠 **Murloc AI Generator**  
- ⏱ **Simple and Date Timers (with TZ support)**  
- 📅 **Static + Dynamic Holidays Engine**  
- 📡 **Automated Daily Broadcasts**  
- 🐉 **Ban’Lu Wisdom Delivery**  
- 🐳 **40MB Optimized Docker Image**  
- ☁️ **Zero-downtime Fly.io Deployment**

The bot architecture prioritizes:

- modularity  
- maintainability  
- predictable async behavior  
- production-ready DevOps practices  

---

# 🚀 Quick Start

## 1. Create a virtual environment
```sh
python3.11 -m venv venv
source venv/bin/activate
```

## 2. Install dependencies
```sh
pip install -r requirements.txt
```

## 3. Configure environment variables
```sh
export DISCORD_BOT_TOKEN="your-token"
export BANLU_CHANNEL_ID="123456"
export HOLIDAYS_CHANNEL_ID="111,222,333"
```

## 4. Start the bot
```sh
python bot.py
```

---

# 📁 Project Structure (Accurate)

```
bot_quote_discord/
│
├── bot.py                        # Application entrypoint
│
├── commands/                     # All bot commands (Cogs)
│     ├── cancel.py
│     ├── date_timer.py
│     ├── help_cmd.py
│     ├── murloc_ai.py
│     ├── quotes.py
│     ├── simple_timer.py
│     └── holidays_cmd.py
│
├── core/                         # Core engine logic
│     ├── dynamic_holidays.py     # Dynamic holiday algorithms (e.g., Easter)
│     ├── helpers.py              # Shared utility functions
│     ├── holidays_flags.py       # Country / religion flag resolver
│     ├── timer_engine.py         # Async timer scheduler engine
│     └── timers.py               # Timer object model
│
├── daily/                        # Scheduled automated tasks
│     ├── banlu/
│     │     └── banlu_daily.py    # Ban'Lu daily post at 10:00 GMT+3
│     └── holidays/
│           └── holidays_daily.py # Holiday broadcast at 10:01 GMT+3
│
├── data/                         # All bot content/data
│     ├── holidays/               # JSON holiday definitions
│     │     ├── Desember.json
│     │     └── ...
│     │
│     ├── murloc_starts.txt       # Murloc AI generator sources
│     ├── murloc_middles.txt
│     ├── murloc_endings.txt
│     ├── quotersbanlu.txt        # Daily Ban’Lu wisdom quotes
│     └── quotes.txt              # General game quotes
│
├── Dockerfile                    # Multi-stage optimized build
├── fly.toml                      # Fly.io Machines configuration
├── requirements.txt              # Dependencies
├── README.md                     # Documentation
└── Murloc-Fulltime-Logo.gif      # Branding asset
```

---

# 🎮 Commands

## 🗨️ Quotes
```
!quote          — random game quote  
!murloc_ai      — generate Murloc wisdom
```

## ⏱ Simple Timer
```
!timer 10m text
```
Supports: `10s`, `5m`, `1h`, `1h20m`, `90`

## 📅 Date Timer
```
!timerdate DD.MM.YYYY HH:MM +TZ text --pin
```

Example:
```
!timerdate 31.12.2025 23:59 +3 New Year! --pin
```

## 🔧 Timer Management
```
!timers          — list active timers  
!cancel <ID>     — cancel one timer  
!cancelall       — clear all timers in the channel
```

---

# 🎉 Holidays System

## Lookup Command
```
!holidays
```

## Features
- Loads all holidays from `data/holidays/*.json`  
- Static (`"12-01"`) and dynamic holidays supported  
- Automatic flag resolution  
- Finds the **nearest upcoming** holiday  
- Supports **multiple holidays** per date  

Example output:
```
🎉 Next Holiday
🇺🇸 Independence Day
📅 Date: 07-04
```

---

# 🔁 Daily Scheduled Tasks (Correct Times)

The bot includes **two independent daily jobs**:

### **🕙 Ban’Lu Daily Quote — 10:00 GMT+3**
Posts one inspirational Ban’Lu quote to the configured channel.  
Source: `data/quotersbanlu.txt`

---

### **🕙 Holiday Broadcast — 10:01 GMT+3**
Checks all holiday JSON files and posts every holiday matching today's date.  
Source folder: `data/holidays/`

**Offline fallback:**  
If the bot was offline at 10:01, the broadcast executes once at startup.

---

# 🔐 Environment Variables

| Variable                | Description                               |
|------------------------|---------------------------------------------|
| `DISCORD_BOT_TOKEN`    | Discord bot token                           |
| `BANLU_CHANNEL_ID`     | Channel ID for Ban’Lu daily quote           |
| `HOLIDAYS_CHANNEL_ID` | Comma-separated list of broadcast channels  |

Example:
```sh
fly secrets set DISCORD_BOT_TOKEN=...
```

---

# 🐳 Deployment (Fly.io Machines)

## Deploy
```sh
fly deploy
```

## View logs
```sh
fly logs
```

## Set secrets
```sh
fly secrets set DISCORD_BOT_TOKEN=...
```

---

# 🧩 Architecture Notes

- Fully async design (asyncio-native)  
- Minimal shared state — loose coupling via module-bound injections  
- Predictable startup/shutdown lifecycle  
- Optimized Docker image (~40 MB)  
- Runs as a non-root user  
- Clean structured logging  
- Production-ready CI/CD pipeline  

---

<p align="center">
  <b>Murloc Edition 🐸 Mrrglglglgl!</b>
</p>
