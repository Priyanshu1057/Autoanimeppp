# Shared configuration for the interactive downloader service.
# Docker Compose supplies per-service BOT_TOKEN and channel variables.
import os

from dotenv import load_dotenv

load_dotenv()

_rss_token = os.environ.get("RSS_BOT_TOKEN", "").strip()
_anime_token = os.environ.get("ANIME_BOT_TOKEN", "").strip()
if _rss_token and _anime_token and _rss_token == _anime_token:
    raise ValueError(
        "RSS_BOT_TOKEN and ANIME_BOT_TOKEN must be different Telegram bot tokens."
    )


def _int_env(name: str, default: int = 0) -> int:
    value = os.environ.get(name, "").strip()
    return int(value) if value else default


API_ID = _int_env("API_ID")
API_HASH = os.environ.get("API_HASH", "").strip()
BOT_TOKEN = (
    os.environ.get("BOT_TOKEN")
    or os.environ.get("ANIME_BOT_TOKEN", "")
).strip()
SET_INTERVAL = max(30, _int_env("SET_INTERVAL", _int_env("ANIME_SET_INTERVAL", 3600)))
TARGET_CHAT_ID = (
    os.environ.get("TARGET_CHAT_ID")
    or os.environ.get("ANIME_TARGET_CHAT_ID", "")
).strip()
MAIN_CHANNEL = (
    os.environ.get("MAIN_CHANNEL")
    or os.environ.get("ANIME_MAIN_CHANNEL", "")
).strip()
LOG_CHANNEL = (
    os.environ.get("LOG_CHANNEL")
    or os.environ.get("ANIME_LOG_CHANNEL", "")
).strip()
MONGO_URL = (
    os.environ.get("MONGO_URL")
    or os.environ.get("MONGO_SRV", "")
).strip()
MONGO_NAME = (
    os.environ.get("MONGO_NAME")
    or os.environ.get("ANIME_MONGO_NAME")
    or "cantarellabots"
).strip()
OWNER_ID = _int_env("OWNER_ID") or _int_env("OWNER")
ADMIN_URL = os.environ.get("ADMIN_URL", "@V_Sbotmaker")
BOT_USERNAME = (
    os.environ.get("BOT_USERNAME")
    or os.environ.get("ANIME_BOT_USERNAME", "")
).strip()
FSUB_PIC = (
    os.environ.get("FSUB_PIC")
    or os.environ.get("ANIME_FSUB_PIC")
    or "https://files.catbox.moe/bli70r.jpg"
)
FSUB_LINK_EXPIRY = max(
    0, _int_env("FSUB_LINK_EXPIRY", _int_env("ANIME_FSUB_LINK_EXPIRY", 600))
)
START_PIC = (
    os.environ.get("START_PIC")
    or os.environ.get("ANIME_START_PIC")
    or "https://files.catbox.moe/4b8jvw.jpg"
)

# Filename and caption templates.
FORMAT = os.environ.get(
    "FORMAT", "[S{season}-E{episode}] {title} [{quality}] [{audio}]"
)
CAPTION = os.environ.get("CAPTION", "[ @cantarellabots {FORMAT}]")
PROGRESS_BAR = os.environ.get(
    "PROGRESS_BAR",
    """
<blockquote>{bar}</blockquote>
<blockquote>📁 <b>{title}</b>
⚡ Speed: {speed}
📦 {current} / {total}</blockquote>
""",
)
RESPONSE_IMAGES = [
    "https://files.catbox.moe/5oonsm.jpg",
    "https://files.catbox.moe/9ufgme.jpg",
    "https://files.catbox.moe/4b8jvw.jpg",
    "https://files.catbox.moe/bli70r.jpg",
    "https://files.catbox.moe/uce0lw.jpg",
    "https://files.catbox.moe/is7q4q.jpg",
]
