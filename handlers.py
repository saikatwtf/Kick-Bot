import logging
import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, PeerIdInvalid

from database import db
from utils import parse_time, is_admin_with_ban_rights, get_bot_privileges

logger = logging.getLogger(__name__)

# Command handlers
async def start_command(client, message):
    """Handle /start command"""
    await message.reply(
        "👋 **Welcome to Kick-Bot!**\n\n"
        "I can help you manage your group by removing inactive users.\n"
        "Type /help to see available commands.\n\n"
        "Join our channel: [AnnihilusOP](https://t.me/AnnihilusOP)"
    )

async def help_command(client, message):
    """Handle /help command"""
    await message.reply(
        "**📚 Kick-Bot Help**\n\n"
        "**Commands:**\n"
        "• /start - Start the bot\n"
        "• /help - Show this help message\n"
        "• /kickinactive [time] - Remove inactive users\n\n"
        "**Time format examples:**\n"
        "• 30s - 30 seconds\n"
        "• 10m - 10 minutes\n"
        "• 6h - 6 hours\n"
        "• 7d - 7 days\n\n"
        "**Note:** The bot needs to be an admin with 'Ban Users' permission to work properly.\n\n"
        "**Join our channel:** [AnnihilusOP](https://t.me/AnnihilusOP)"
    )

async def kick_inactive_command(client, message):
    """Handle /kickinactive command"""
    # Debug log to help troubleshoot chat type issues
    logger.info(f"Chat type: {message.chat.type}, Chat ID: {message.chat.id}, Chat title: {message.chat.title}")
    
    # Check if command is used in a group - use a more reliable method
    if not message.chat or message.chat.id > 0:  # Positive IDs are private chats
        await message.reply("This command can only be used in groups.")
        return

    # Check if user is admin with ban rights
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not await is_admin_with_ban_rights(client, chat_id, user_id):
        await message.reply("You need to be an admin with 'Ban Users' permission to use this command.")
        return
    
    # Check if bot has ban rights
    bot_privileges = await get_bot_privileges(client, chat_id)
    if not bot_privileges.can_restrict_members:
        await message.reply("I need 'Ban Users' permission to remove inactive users.")
        return
    
    # Parse time parameter
    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.reply(
            "Please specify a time period.\n"
            "Example: `/kickinactive 7d` to remove users inactive for 7 days."
        )
        return
    
    time_str = command_parts[1]
    time_delta = parse_time(time_str)
    
    if not time_delta:
        await message.reply(
            "Invalid time format. Use format like:\n"
            "• 30s (seconds)\n"
            "• 10m (minutes)\n"
            "• 6h (hours)\n"
            "• 7d (days)"
        )
        return
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - time_delta
    
    # Get inactive users
    status_msg = await message.reply("Searching for inactive users...")
    
    inactive_users = await db.get_inactive_users(chat_id, cutoff_time)
    
    if not inactive_users:
        await status_msg.edit_text("No inactive users found.")
        return
    
    # Create confirmation message with inline keyboard
    confirm_text = f"Found {len(inactive_users)} users inactive for more than {time_str}.\n\nDo you want to remove them?"
    
    await status_msg.edit_text(
        confirm_text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Yes", callback_data=f"kick_confirm_{time_str}"),
                InlineKeyboardButton("No", callback_data="kick_cancel")
            ]
        ])
    )

# Callback query handler for kick confirmation
async def kick_confirm_callback(client, callback_query):
    """Handle kick confirmation callback"""
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    
    # Check if user is admin with ban rights
    if not await is_admin_with_ban_rights(client, chat_id, user_id):
        await callback_query.answer("You don't have permission to do this.", show_alert=True)
        return
    
    if data == "kick_cancel":
        await callback_query.message.edit_text("Operation cancelled.")
        return
    
    if data.startswith("kick_confirm_"):
        time_str = data.split("_")[2]
        time_delta = parse_time(time_str)
        
        if not time_delta:
            await callback_query.message.edit_text("Invalid time format.")
            return
        
        # Calculate cutoff time
        cutoff_time = datetime.now() - time_delta
        
        # Get inactive users
        await callback_query.message.edit_text("Processing inactive users...")
        
        inactive_users = await db.get_inactive_users(chat_id, cutoff_time)
        
        if not inactive_users:
            await callback_query.message.edit_text("No inactive users found.")
            return
        
        # Kick inactive users
        kicked_count = 0
        failed_count = 0
        
        for user in inactive_users:
            try:
                # Skip admins
                member = await client.get_chat_member(chat_id, user["user_id"])
                if member.privileges:  # If user has any privileges, they're an admin
                    continue
                
                # Kick user
                await client.ban_chat_member(chat_id, user["user_id"])
                await client.unban_chat_member(chat_id, user["user_id"])  # Unban to allow rejoin
                kicked_count += 1
                
                # Add delay to avoid flood limits
                await asyncio.sleep(0.5)
            except UserAdminInvalid:
                # User is an admin
                continue
            except (ChatAdminRequired, PeerIdInvalid) as e:
                logger.error(f"Failed to kick user {user['user_id']}: {e}")
                failed_count += 1
        
        result_text = f"Operation completed.\n\n"
        result_text += f"• Removed: {kicked_count} users\n"
        if failed_count > 0:
            result_text += f"• Failed: {failed_count} users\n"
        
        await callback_query.message.edit_text(result_text)

# Message handler to track user activity
async def track_user_activity(client, message):
    """Track user activity based on messages"""
    if not message.from_user or message.from_user.is_bot:
        return
    
    # Skip tracking for commands
    if message.text and message.text.startswith("/"):
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Update user's last activity
    await db.update_user_activity(chat_id, user_id, username, first_name)

def register_handlers(app):
    """Register all message handlers"""
    # Command handlers
    app.on_message(filters.command("start"))(start_command)
    app.on_message(filters.command("help"))(help_command)
    app.on_message(filters.command("kickinactive"))(kick_inactive_command)
    
    # Callback query handler
    app.on_callback_query(filters.regex(r"^kick_(confirm|cancel)"))(kick_confirm_callback)
    
    # Message handler for tracking activity
    app.on_message(filters.group & ~filters.service & ~filters.me & ~filters.bot)(track_user_activity)