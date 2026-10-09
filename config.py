# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KONFIGURASI TELEGRAM PROFILE ROTATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1. Kredensial Telegram (dapatkan dari https://my.telegram.org)
API_ID   = 123456
API_HASH = "xxxxxxx"

# 2. Nama sesi file Telethon
SESSION_NAME = "profile_rotate"

# 3. File penyimpan state slot foto profil aktif
STATE_FILE = "profile_rotate_state.json"

# 4. Durasi jeda acak rotasi profil (dalam detik)
MIN_ROTATE_INTERVAL_SEC = 15 * 60  # 15 menit
MAX_ROTATE_INTERVAL_SEC = 20 * 60  # 20 menit
