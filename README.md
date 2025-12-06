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
* 🧠 **Murloc AI** — generates Murloc wisdom on demand
* ⏱ **Timers** — simple timers and date-based GMT timers
* 📌 **Pin Support** — optional auto-pin for date timers
* 🔁 **Daily Scheduler** — Ban’Lu quotes sent every morning
* 🐳 **Optimized Docker Image** (~35–40 MB)
* ☁️ **Fully Deployable on Fly.io**
* 🔐 **Secure Secret Handling**
* ⚙️ **CI/CD Ready**

---

## 🏗 Tech Stack

| Component          | Choice             | Reason                              |
| ------------------ | ------------------ | ----------------------------------- |
| **Language**       | Python 3.11        | Modern, efficient, widely supported |
| **Library**        | discord.py 2.x     | Reliable, async-ready Discord API   |
| **Infrastructure** | Fly.io Machines    | Perfect for 24/7 bots               |
| **Runtime**        | Docker multi-stage | Small, reproducible builds          |
| **CI/CD**          | GitHub Actions     | Automated deploy pipeline           |

---

## 📁 Project Structure

```
bot_quote_discord/
│
├── bot.py                 # Main entry point
├── Dockerfile             # Multi-stage Docker build
├── fly.toml               # Fly.io configuration
├── requirements.txt       # Dependencies
├── .dockerignore          # Docker context ignore rules
│
├── core/                  # Core logic (timers, helpers)
├── commands/              # Slash-like prefix commands
├── daily/                 # Scheduled tasks (Ban'Lu)
├── data/                  # Static text files
│
└── .github/workflows/
       └── fly-deploy.yml  # CI/CD pipeline
```

---

## 🔐 Environment Variables

| Variable            | Description                 |
| ------------------- | --------------------------- |
| `DISCORD_BOT_TOKEN` | Your Discord bot token      |
| `BANLU_CHANNEL_ID`  | Channel ID for daily quotes |
| `BANLU_QUOTES_FILE` | Path to Ban’Lu quotes file  |

Set secrets on Fly.io:

```sh
fly secrets set DISCORD_BOT_TOKEN="YOUR_TOKEN"
```

---

## 🧪 Local Development

### Run directly:

```sh
export DISCORD_BOT_TOKEN="YOUR_TOKEN"
python bot.py
```

### Run via Docker:

```sh
docker build -t bot_local .
docker run --rm -it \
  -e DISCORD_BOT_TOKEN="YOUR_TOKEN" \
  bot_local
```

---

## ☁️ Deployment (Fly.io)

### 1. Deploy

```sh
fly deploy
```

### 2. Set secrets

```sh
fly secrets set DISCORD_BOT_TOKEN="YOUR_TOKEN"
```

### 3. View logs

```sh
fly logs
```

> The bot will stay online 24/7 on Fly.io Machines.

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

## 🔁 Daily Ban’Lu Quotes

Automatically posts a themed quote every day at **10:00 MSK**.

Triggered via:

* automated scheduler
* fallback: sends once if bot missed the scheduled time

---

## 🧭 Roadmap

* Slash commands version
* Quote categories & packs
* Optional database backend
* Webhooks for external integrations
* Dashboard UI (planned)

---

## 📝 License

MIT
Feel free to use, modify, and contribute!

---

<p align="center">
  <b>Murloc Edition 🐸 Mrrglglglgl! </b>
</p>
