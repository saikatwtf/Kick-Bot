import re
from datetime import datetime, timedelta
from pyrogram.types import ChatPrivileges

def parse_time(time_str):
    """
    Parse time string in format like '30s', '5m', '2h', '1d'
    Returns timedelta object or None if invalid format
    """
    if not time_str:
        return None
    
    match = re.match(r'^(\d+)([smhd])$', time_str.lower())
    if not match:
        return None
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 's':
        return timedelta(seconds=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    
    return None

async def is_admin_with_ban_rights(client, chat_id, user_id):
    """Check if the user is an admin with ban rights"""
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.privileges:
            return member.privileges.can_restrict_members
        return False
    except Exception:
        return False

async def get_bot_privileges(client, chat_id):
    """Get the bot's privileges in the chat"""
    try:
        bot_id = (await client.get_me()).id
        member = await client.get_chat_member(chat_id, bot_id)
        return member.privileges
    except Exception:
        return ChatPrivileges(can_restrict_members=False)