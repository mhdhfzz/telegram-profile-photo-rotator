from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print("=" * 60)
print("  Telegram StringSession Generator (Cloudflare Worker)")
print("=" * 60)

api_id_input = input("Masukkan API_ID: ").strip()
api_hash_input = input("Masukkan API_HASH: ").strip()

if not api_id_input or not api_hash_input:
    print("❌ API_ID dan API_HASH tidak boleh kosong!")
    exit(1)

api_id = int(api_id_input)
api_hash = api_hash_input

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n✅ BERHASIL LOGIN!")
    print("Salin string di bawah ini untuk STRING_SESSION Cloudflare Workers:")
    print("-" * 65)
    print(client.session.save())
    print("-" * 65)
