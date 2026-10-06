# Combined AutoAnimeBot deployment

This repository keeps the original automatic RSS publisher and adds the
interactive AniWatch/Animetsu search-and-download bot. Run them as separate
services: they use different Telegram client libraries and **must use different
bot tokens**.

## Requirements

- Docker Engine and Docker Compose v2
- A Telegram API ID/hash from [my.telegram.org](https://my.telegram.org)
- Two bot tokens from [@BotFather](https://t.me/BotFather)
- A MongoDB URI
- The RSS publisher's Telegram channels, with the RSS bot promoted as an admin
- Adequate disk space and network capacity for media downloads and encoding

## Configure

1. Copy `.env.example` to `.env`.
2. Fill in `API_ID`, `API_HASH`, `OWNER_ID`, and `MONGO_URL`.
3. Set `RSS_BOT_TOKEN` and `ANIME_BOT_TOKEN` to **different** bot tokens.
4. Set the four `RSS_*_CHANNEL` IDs. Promote the RSS bot in each channel.
5. Optionally set the `ANIME_*_CHANNEL` IDs for downloader logs and channel
   posts. Leave `ANIME_TARGET_CHAT_ID` blank to deliver manual downloads to the
   user who requested them.

Never commit `.env` or publish bot tokens/MongoDB credentials.

## Run

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f
```

To stop both services:

```bash
docker compose down
```

The Compose file builds each service with its own Python runtime and
requirements. The downloader image fetches the pinned Linux
`N_m3u8DL-RE` release during the image build. The downloader's optional health
endpoint is exposed on host port `ANIME_HEALTH_PORT` (8080 by default).
The current downloader image targets Linux/amd64 because that is the upstream
binary bundled by its scraper; ARM deployment needs an ARM-compatible
`N_m3u8DL-RE` build and a matching Dockerfile.

## Included workflows

- **RSS publisher:** polls SubsPlease, downloads releases, encodes them, and
  publishes to configured Telegram channels.
- **Interactive downloader:** search by title or URL; choose episodes,
  resolution, and batch/range downloads; browse favorites; use schedule and
  ongoing tracking; configure admins, bans, force-subscription channels,
  mappings, broadcasts, settings, status, and automatic deletion.
- **Deployment:** two independently restartable Docker services and isolated
  dependency sets to avoid the original Pyrogram/Kurigram conflict.

## Use the interactive bot

- `/start` and `/help` show the welcome and help menus.
- Send an anime title or supported AniWatch/Animetsu URL to search. In the
  upstream implementation, search and downloads are restricted to the owner
  and configured admins.
- Use the inline episode controls for single episodes, quality selection,
  whole-season downloads, or a selected episode range.
- `/schedule` (or `/ongoing`) shows the day's schedule; `/favorites` lists saved
  anime for admins.
- Admins can use `/manage`, `/autodel <seconds>`, `/stats`, `/ping`,
  `/admins`, and `/users`. The owner can use `/add_admin <user_id>` and
  `/rm_admin <user_id>`.
- Ongoing scraping in the interactive service is off by default. Set
  `ANIME_TARGET_CHAT_ID`, then enable it from `/manage` if you want it. The
  original RSS publisher remains a separate always-running service.

The source scrapers depend on third-party sites and may stop working if those
sites change. Only download or redistribute media where you have the necessary
rights.
