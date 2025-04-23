import logging
from bot import create_bot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Create and run the bot
    bot = create_bot()
    logger.info("Bot started successfully!")
