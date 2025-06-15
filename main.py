import asyncio
import logging
from pyrogram import Client, idle
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid

from config import API_ID, API_HASH, BOT_TOKEN, BOT_USERNAME
import config
from database import db
from handlers import register_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Start the bot"""
    # Initialize the client
    app = Client(
        "kick_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )
    
    try:
        # Connect to database
        await db.connect()
        
        # Start the client
        await app.start()
        
        # Get bot info and set username
        me = await app.get_me()
        config.BOT_USERNAME = me.username
        logger.info(f"Bot started as @{me.username}")
        
        # Register handlers
        register_handlers(app)
        
        # Keep the bot running
        await idle()
    except (ApiIdInvalid, ApiIdPublishedFlood):
        logger.error("API ID/Hash is invalid or published. Check your credentials.")
    except AccessTokenInvalid:
        logger.error("Bot token is invalid. Check your bot token.")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        # Close the database connection
        await db.close()
        
        # Stop the client
        if app.is_connected:
            await app.stop()

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())