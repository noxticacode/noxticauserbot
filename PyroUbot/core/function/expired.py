import asyncio
import time
import logging
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup
from pytz import timezone

from PyroUbot import *

# Set up logger for tracking expiry operations
expiry_logger = logging.getLogger('expiry_operations')
expiry_logger.setLevel(logging.INFO)

# In-memory cache to track processing
_processing_users = set()
_last_error_time = {}

async def expiredUserbots():
    """
    Checks for expired userbots and handles them gracefully.
    Improved: Handles users with NO expiry date by removing them.
    """
    # Timeout between full scan cycles (5 minutes)
    SCAN_INTERVAL = 300
    
    # Maximum time to process a single user (to prevent hanging)
    MAX_USER_PROCESS_TIME = 30
    
    print("[INFO] Starting expired userbot monitoring service")
    
    while True:
        try:
            # Get current time in target timezone
            current_time = datetime.now(timezone("Asia/Jakarta"))
            current_date = current_time.strftime("%d-%m-%Y")
            
            # Process users in smaller batches
            active_ubots = list(ubot._ubot)
            batch_size = min(5, len(active_ubots))
            
            print(f"[INFO] Checking expiry status for {len(active_ubots)} userbots")
            
            # Process each userbot in batches
            for i in range(0, len(active_ubots), batch_size):
                batch = active_ubots[i:i+batch_size]
                
                for X in batch:
                    if not X or not hasattr(X, 'me') or not hasattr(X.me, 'id'):
                        continue
                        
                    user_id = X.me.id
                    
                    # Skip if already being processed
                    if user_id in _processing_users:
                        continue
                    
                    # Rate limit error messages (300 seconds)
                    now = time.time()
                    if user_id in _last_error_time and now - _last_error_time.get(user_id, 0) < 300:
                        continue
                    
                    try:
                        _processing_users.add(user_id)
                        
                        # Use a timeout to prevent hanging on a single user
                        async def process_user():
                            try:
                                # Jangan cek expired untuk Owner agar tidak terhapus sendiri
                                if user_id == OWNER_ID:
                                    return

                                exp_date = await get_expired_date(user_id)
                                
                                # === LOGIKA BARU: JIKA TIDAK ADA TANGGAL, ANGGAP EXPIRED ===
                                if not exp_date:
                                    print(f"[INFO] - {user_id} - No expiry date found (Illegal User) - REMOVING")
                                    await process_expired_user(X, user_id)
                                    return
                                
                                exp_str = exp_date.strftime("%d-%m-%Y")
                                
                                # Check if expired today
                                if current_date == exp_str:
                                    print(f"[INFO] - {user_id} - EXPIRY DETECTED ({exp_str})")
                                    await process_expired_user(X, user_id)
                                    
                            except Exception as e:
                                _last_error_time[user_id] = now
                                print(f"[ERROR] - {user_id} - Failed to check expiry: {str(e)}")
                        
                        try:
                            # Run with timeout
                            await asyncio.wait_for(process_user(), timeout=MAX_USER_PROCESS_TIME)
                        except asyncio.TimeoutError:
                            _last_error_time[user_id] = now
                            print(f"[ERROR] - {user_id} - Processing timed out after {MAX_USER_PROCESS_TIME}s")
                    
                    finally:
                        # Always remove from processing set
                        if user_id in _processing_users:
                            _processing_users.remove(user_id)
                
                # Add small delay between batches
                if i + batch_size < len(active_ubots):
                    await asyncio.sleep(2)
            
            # Wait before next full scan
            print(f"[INFO] Completed expiry check, next scan in {SCAN_INTERVAL // 60} minutes")
            await asyncio.sleep(SCAN_INTERVAL)
            
        except Exception as e:
            print(f"[CRITICAL] Error in expiredUserbots main loop: {str(e)}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(60)

async def process_expired_user(client, user_id):
    """Process a single expired user with comprehensive error handling"""
    steps_completed = []
    
    try:
        # Step 1: Unblock the bot
        try:
            await client.unblock_user(bot.me.username)
            steps_completed.append("unblock")
        except Exception as e:
            pass
        
        # Step 2: Remove user from database
        try:
            await remove_ubot(user_id)
            steps_completed.append("remove_db")
        except Exception as e:
            print(f"[ERROR] - {user_id} - Failed to remove from database: {str(e)}")
        
        # Step 3: Remove variables
        try:
            await remove_all_vars(user_id)
            steps_completed.append("remove_vars")
        except Exception as e:
            print(f"[ERROR] - {user_id} - Failed to remove variables: {str(e)}")
        
        # Step 4: Remove expiry date
        try:
            await rem_expired_date(user_id)
            steps_completed.append("remove_expiry")
        except Exception as e:
            print(f"[ERROR] - {user_id} - Failed to remove expiry data: {str(e)}")

        # Step 4.5: Remove Premium Status (Tambahan)
        try:
            await remove_vars(bot.me.id, "PREM_USERS", user_id) # Menghapus dari list prem jika ada
            steps_completed.append("remove_prem_status")
        except Exception:
            pass
        
        # Step 5: Remove from memory lists
        try:
            if user_id in ubot._get_my_id:
                ubot._get_my_id.remove(user_id)
            steps_completed.append("remove_id")
        except Exception:
            pass
        
        try:
            if client in ubot._ubot:
                ubot._ubot.remove(client)
            steps_completed.append("remove_client")
        except Exception:
            pass
        
        # Step 6: Send notification message (Suruh beli lagi)
        try:
            await bot.send_message(
                user_id,
                f"""
<b>Masa aktif Userbot Anda telah berakhir atau tidak valid!</b>

Silahkan melakukan pembelian ulang untuk melanjutkan penggunaan bot ini.
                """,
                reply_markup=InlineKeyboardMarkup(BTN.EXP_UBOT()),
            )
            steps_completed.append("notify")
        except Exception as e:
            print(f"[ERROR] - {user_id} - Failed to send notification: {str(e)}")

        # Step 7: Log out client (Final Step)
        try:
            await client.log_out()
            steps_completed.append("logout")
        except Exception as e:
            print(f"[ERROR] - {user_id} - Failed to log out: {str(e)}")
        
        # Final confirmation
        print(f"[INFO] - {user_id} - EXPIRED END - Steps completed: {', '.join(steps_completed)}")
        
    except Exception as e:
        print(f"[CRITICAL] - {user_id} - Failed to process expiry: {str(e)}")
