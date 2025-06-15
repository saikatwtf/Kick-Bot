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
        # Check for different member types since Pyrogram API might return different objects
        if hasattr(member, 'privileges') and member.privileges:
            return member.privileges.can_restrict_members
        # For older Pyrogram versions or different chat member types
        if member.status in ["creator", "administrator"]:
            if hasattr(member, 'can_restrict_members'):
                return member.can_restrict_members
            # Creator always has all rights
            if member.status == "creator":
                return True
        return False
    except Exception as e:
        print(f"Error checking admin rights: {e}")
        return False

async def get_bot_privileges(client, chat_id):
    """Get the bot's privileges in the chat"""
    try:
        bot_id = (await client.get_me()).id
        member = await client.get_chat_member(chat_id, bot_id)
        
        # Handle different member types
        if hasattr(member, 'privileges') and member.privileges:
            return member.privileges
        
        # For older Pyrogram versions or different chat member types
        if member.status in ["creator", "administrator"]:
            # Create a custom privileges object
            privileges = ChatPrivileges()
            if hasattr(member, 'can_restrict_members'):
                privileges.can_restrict_members = member.can_restrict_members
            # Creator always has all rights
            elif member.status == "creator":
                privileges.can_restrict_members = True
            return privileges
            
        return ChatPrivileges(can_restrict_members=False)
    except Exception as e:
        print(f"Error getting bot privileges: {e}")
        return ChatPrivileges(can_restrict_members=False)