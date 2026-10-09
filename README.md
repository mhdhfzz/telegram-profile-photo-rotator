# Telegram Profile Photo Rotator

Skrip otomatis untuk mengganti atau merotasi foto profil akun Telegram secara berkala dengan jeda acak 15 sampai 20 menit.

---

## Bagaimana Cara Kerjanya?

Bot ini **tidak mengunggah gambar baru dari penyimpanan lokal** setiap kali berganti. Cara kerjanya adalah memanfaatkan riwayat foto profil yang **sudah ada di akun Telegram Anda**:

1. Pastikan akun Telegram Anda sudah memiliki minimal 2 foto profil (atau lebih).
2. Bot akan membaca daftar foto profil Anda lewat MTProto API.
3. Setiap 15–20 menit sekali, bot akan memindahkan foto berikutnya ke posisi paling depan (menjadikannya foto profil utama).
4. Rentang jeda 15–20 menit sengaja dipilih acak agar aktivitas akun terlihat wajar dan terhindar dari pembatasan (*FloodWait*) oleh Telegram.

Anda bisa menjalankannya lewat dua metode:
- **VPS Linux / Komputer Lokal (Python Telethon)**: Paling mudah jika punya VPS sendiri, bisa langsung jalan sebagai background service systemd.
- **Cloudflare Worker (JavaScript Serverless)**: Pilihan gratis tanpa perlu sewa VPS sama sekali.

---

## Persiapan Awal

Sebelum mulai, Anda membutuhkan `API_ID` dan `API_HASH` dari Telegram:

1. Kunjungi portal resmi: [my.telegram.org](https://my.telegram.org).
2. Masukkan nomor HP akun Telegram Anda (misal: `+6281234567890`), lalu login dengan kode yang dikirim ke aplikasi Telegram.
3. Masuk ke bagian **API development tools**.
4. Isi formulir pembuatan aplikasi (nama app dan short name bebas, platform pilih `Desktop` atau `Other`).
5. Simpan nilai **App api_id** dan **App api_hash** yang diberikan.

> **Catatan:** Jangan pernah membagikan `API_HASH` atau string sesi login ke orang lain atau mempublikasikannya di repository publik.

---

## Metode 1: VPS Linux / Komputer Lokal (Python)

Metode ini menggunakan skrip Python (`Telethon`) dan cocok dijalankan 24/7 di server VPS.

### 1. Pasang Dependensi
```bash
pip install telethon
# atau jika di Linux/Ubuntu:
pip3 install telethon
```

### 2. Isi Kredensial
Buka file `config.py` dan masukkan `API_ID` serta `API_HASH` Anda:
```python
API_ID = 12345678
API_HASH = "b78a9c01f2e456..."
```

### 3. Tes Login Pertama Kali
Jalankan bot sekali untuk memasukkan nomor telepon dan kode OTP Telegram:
```bash
python main.py
```
Setelah bot berhasil login dan rotasi pertama selesai, tekan `Ctrl + C` untuk keluar. File sesi login Anda kini sudah tersimpan secara lokal.

### 4. Pasang Sebagai Service Otomatis di VPS
Agar bot terus berjalan di latar belakang dan otomatis menyala kembali jika server reboot:
```bash
bash install_service.sh
```
*(Skrip otomatis mendeteksi izin root/sudo dan path Python yang terpasang).*

**Perintah pengelolaan service:**
- Cek status: `sudo systemctl status telegram-profile-rotator`
- Cek log berjalan: `sudo journalctl -u telegram-profile-rotator -f`
- Restart bot: `sudo systemctl restart telegram-profile-rotator`
- Hentikan bot: `sudo systemctl stop telegram-profile-rotator`

---

## Metode 2: Cloudflare Worker (Serverless & Gratis)

Jika tidak memiliki server VPS, Anda bisa menjalankannya di Cloudflare Workers.

### 1. Buat String Sesi Login
Jalankan skrip bantuan untuk menghasilkan string sesi:
```bash
python export_session.py
```
Masukkan `API_ID`, `API_HASH`, nomor HP, dan kode OTP. Salin string panjang `STRING_SESSION` yang ditampilkan di terminal.

### 2. Atur di Dashboard Cloudflare
1. Buka [dash.cloudflare.com](https://dash.cloudflare.com) lalu masuk ke menu **Workers & Pages** > **KV**.
2. Buat namespace baru dengan nama `USERBOT_KV`.
3. Masuk ke **Workers & Pages** > **Create application** > **Create Worker**, beri nama (contoh: `telegram-rotator`), lalu deploy.
4. Masuk ke halaman Worker tersebut > **Settings** > **Variables and KV**:
   - Di bagian **KV Namespace Bindings**, sambungkan variable `USERBOT_KV` ke namespace KV yang baru dibuat tadi.
   - Di bagian **Environment Variables / Secrets**, tambahkan 3 variabel berikut:
     - `API_ID`: ID API Telegram Anda.
     - `API_HASH`: Hash API Telegram Anda.
     - `STRING_SESSION`: String sesi dari Langkah 1.
5. Masuk ke **Settings** > **Configuration** (atau **Runtime**), lalu aktifkan fitur **Node.js compatibility** (`nodejs_compat`).
6. Buka tab editor kode (**Edit code**), ganti kode default dengan seluruh isi file `worker.js`, lalu klik **Save and deploy**.

### 3. Mengaktifkan Rotasi
Buka URL Worker Anda di browser pada path `/rotate`:
```text
https://telegram-rotator.<subdomain>.workers.dev/rotate
```
- Bot akan aktif, melakukan rotasi pertama, dan menampilkan dashboard status dengan hitung mundur langsung (*real-time countdown*).
- **Opsi A (24/7 Otomatis Penuh di Cloudflare - Dianjurkan):**
  Di halaman Worker Cloudflare, buka **Settings** > **Triggers** > **Cron Triggers** > **Add Cron Trigger**, masukkan ekspresi `*/5 * * * *` (setiap 5 menit). Cloudflare akan otomatis memeriksa dan merotasi foto profil di latar belakang tanpa perlu membuka browser sama sekali.
- **Opsi B (Tanpa Cron Trigger):**
  Biarkan tab browser dashboard tetap terbuka (halaman otomatis me-refresh dan merotasi foto ketika waktu hitung mundur habis), atau akses URL `/status` kapan saja untuk memicu rotasi otomatis jika jadwal sudah tiba.
- **Daftar Endpoint:**
  - Status aktif & hitung mundur: `/status` *(otomatis merotasi foto jika waktu tunggu habis)*
  - Rotasi paksa sekarang: `/rotate`
  - Hentikan rotasi: `/stop`

---

## Ringkasan Berkas

- `main.py`: Skrip bot utama untuk versi Python / VPS.
- `config.py`: File konfigurasi kredensial untuk versi VPS.
- `install_service.sh`: Skrip instalasi otomatis systemd service di VPS Linux.
- `export_session.py`: Skrip CLI untuk menghasilkan `STRING_SESSION` bagi Cloudflare Worker.
- `worker.js`: Skrip bot serverless untuk Cloudflare Workers.
- `profile_rotate_state.json`: File penyimpan status slot rotasi aktif di lingkungan lokal/VPS.