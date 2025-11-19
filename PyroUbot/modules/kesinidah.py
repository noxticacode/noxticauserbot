from PyroUbot import *
from pyrogram import enums

__MODULE__ = "kesinidah"
__HELP__ = """
<b>Bantuan untuk kesinidah</b>

<b>Perintah :</b>
• <code>{0}kesinidah</code>: Membuat semua client join ke grup dimana perintah itu dijalankan.

<b>Hanya untuk Owner.</b>
"""

@PY.UBOT("kesinidah")
@PY.OWNER
async def _(client, message):
    try:
        if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply("Perintah ini hanya dapat digunakan di grup.")
            return

        chat_id = message.chat.id
        
        # Dapatkan tautan undangan grup
        try:
            invite_link = await client.export_chat_invite_link(chat_id)
        except Exception as e:
            await message.reply(f"Gagal mendapatkan tautan undangan: {e}")
            return

        for ubot_client in ubot._ubot:
            try:
                await ubot_client.join_chat(invite_link)
            except Exception as e:
                # Lewati jika sudah menjadi anggota
                if "already" in str(e).lower():
                    continue
                else:
                    print(f"Gagal bergabung dengan {ubot_client.me.id}: {e}")
        
        await message.reply("Semua client telah diperintahkan untuk bergabung ke grup ini.")

    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {e}")
