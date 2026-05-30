import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# System Variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Discord Keybind Macros
DISCORD_MACROS = {
    "mute": "ctrl+shift+m",
    "unmute": "ctrl+shift+m",
    "share screen": "ctrl+shift+o",
    "stop sharing": "ctrl+shift+o"
}