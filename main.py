import os
import sys
import asyncio
import json
import random
from datetime import datetime

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.photos import (
    GetUserPhotosRequest,
    UpdateProfilePhotoRequest,
)
from telethon.tl.types import InputPhoto

from config import (
    API_ID,
    API_HASH,
    SESSION_NAME,
    STATE_FILE,
    MIN_ROTATE_INTERVAL_SEC,
    MAX_ROTATE_INTERVAL_SEC,
)

# ---------------------------------------------------------------------------
# Telegram Client
# ---------------------------------------------------------------------------

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


# ==========================
# STATE MANAGEMENT
# ==========================
def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {"current_slot": 0}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"current_slot": 0}


def save_state(data: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ==========================
# ROTATED PROFILE
# ==========================
def format_duration_short(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


async def rotate_profile() -> None:
    state = load_state()
    try:
        result = await client(
            GetUserPhotosRequest(
                user_id="me",
                offset=0,
                max_id=0,
                limit=100,
            )
        )

        photos = result.photos

        if len(photos) < 2:
            print(f"[{datetime.now()}] Minimal perlu 2 foto profil agar rotasi dapat berjalan.", flush=True)
            return

        slot = state.get("current_slot", 0) % len(photos)
        target_photo = photos[slot]

        input_photo = InputPhoto(
            id=target_photo.id,
            access_hash=target_photo.access_hash,
            file_reference=target_photo.file_reference,
        )

        await client(UpdateProfilePhotoRequest(id=input_photo))

        state["current_slot"] = slot + 1
        save_state(state)

        print(
            f"[{datetime.now()}] "
            f"Profile updated (slot {slot + 1}/{len(photos)})",
            flush=True,
        )
    except FloodWaitError as e:
        print(f"[{datetime.now()}] [WARNING] Terkena FloodWait! Durasi pembatasan {format_duration_short(e.seconds)}", flush=True)
        print(f"[{datetime.now()}] [INFO] Jeda sementara untuk keamanan akun...", flush=True)
        await asyncio.sleep(e.seconds + 5)
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Terjadi kesalahan: {e}", flush=True)
        print("[INFO] Mencoba kembali dalam 60 detik...", flush=True)
        await asyncio.sleep(60)


# ==========================
# LOOP
# ==========================
async def rotation_loop() -> None:
    while True:
        try:
            await rotate_profile()
        except Exception as e:
            print(f"[{datetime.now()}] Rotation error: {e}", flush=True)

        interval = random.randint(MIN_ROTATE_INTERVAL_SEC, MAX_ROTATE_INTERVAL_SEC)
        print(f"[{datetime.now()}] Jeda rotasi berikutnya: {format_duration_short(interval)}", flush=True)
        await asyncio.sleep(interval)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main() -> None:
    print("=" * 45, flush=True)
    print("  Telegram Profile Photo Rotator (Telethon) Aktif", flush=True)
    print("  Ctrl+C   : berhenti", flush=True)
    print("=" * 45, flush=True)

    await client.start()
    await rotation_loop()
    await client.run_until_disconnected()


if __name__ == "__main__":
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")
    asyncio.run(main())
