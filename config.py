import os

# Telegram Bot Token
BOT_TOKEN = "7304877490:AAFARg_AEiQZZlajoauWKsCMSOfzjosG4e0"

# Maximum file size (in bytes) - 20MB
MAX_FILE_SIZE = 20 * 1024 * 1024

# Temporary directory for file processing
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Default language
DEFAULT_LANGUAGE = "ar"  # Arabic

# Admin user ID (change this to your Telegram user ID)
ADMIN_ID = 7089656746  # معرف مدير البوت على تيليجرام (@Mavdiii)
