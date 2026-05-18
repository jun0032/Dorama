# 🎵 OST Bot

A Discord bot for K-Drama fans that bridges the gap between what you're watching and what you're listening to.

## Features

| Command | Description | Status |
|---|---|---|
| `/ping` | Check if the bot is online | ✅ Phase 1 |
| `/help` | See all commands | ✅ Phase 1 |
| `/watchlist add` | Save a drama to your watchlist | ✅ Phase 1 |
| `/watchlist show` | View your saved dramas | ✅ Phase 1 |
| `/watchlist remove` | Remove a drama from your watchlist | ✅ Phase 1 |
| `/drama [name]` | Look up a K-Drama | 🔧 Phase 2 |
| `/ost [drama]` | Get the soundtrack on Spotify | 🔧 Phase 3 |
| `/recommend [mood]` | AI-powered drama + OST recommendation | 🔧 Phase 4 |

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/ost-bot.git
cd ost-bot
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API keys
```bash
cp .env.example .env
```
Then fill in your keys in `.env`:
- **DISCORD_TOKEN** — [Discord Developer Portal](https://discord.com/developers/applications)
- **SPOTIFY_CLIENT_ID / SECRET** — [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- **ANTHROPIC_API_KEY** — [Anthropic Console](https://console.anthropic.com)

### 5. Run the bot
```bash
python main.py
```

## Project Structure

```
ost-bot/
├── main.py           # Bot entry point
├── database.py       # SQLite watchlist logic
├── requirements.txt
├── .env.example
├── cogs/
│   ├── drama.py      # /drama command (Phase 2)
│   ├── ost.py        # /ost command (Phase 3)
│   ├── recommend.py  # /recommend command (Phase 4)
│   └── watchlist.py  # /watchlist commands
└── utils/            # API helpers (Phase 2+)
```

## Tech Stack

- **discord.py** — Discord bot framework
- **SQLite** — Watchlist persistence
- **spotipy** — Spotify API (Phase 3)
- **anthropic** — Claude AI recommendations (Phase 4)
- **aiohttp** — HTTP requests for MDL (Phase 2)
