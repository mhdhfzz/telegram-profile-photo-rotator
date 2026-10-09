#!/bin/bash
# =========================================================================
#  Otomatisasi Instalasi Service Systemd: Telegram Profile Photo Rotator
# =========================================================================

set -e

# Deteksi hak akses root / sudo otomatis
SUDO=""
if [ "$EUID" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    echo "❌ Akses root diperlukan untuk memasang service di /etc/systemd/system/."
    echo "   Silakan login sebagai root atau gunakan perintah dengan sudo."
    exit 1
  fi
fi

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Dukung 'python3' maupun 'python' (pilih yang tersedia)
PYTHON_PATH="$(command -v python3 || command -v python || true)"

if [ -z "$PYTHON_PATH" ]; then
  echo "❌ python3 atau python tidak ditemukan di sistem!"
  exit 1
fi

RUN_USER="${SUDO_USER:-$USER}"
SERVICE_NAME="telegram-profile-rotator.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

echo "============================================="
echo "  Instalasi Systemd Service: $SERVICE_NAME"
echo "============================================="
echo "📁 Direktori bot : $CURRENT_DIR"
echo "🐍 Python binary : $PYTHON_PATH ($($PYTHON_PATH --version 2>&1))"
echo "👤 User service  : $RUN_USER"
echo "============================================="

$SUDO tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Telegram Profile Photo Rotator
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$RUN_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$PYTHON_PATH main.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "Mengaktifkan service..."
$SUDO systemctl daemon-reload
$SUDO systemctl enable "$SERVICE_NAME"
$SUDO systemctl restart "$SERVICE_NAME"

echo ""
echo "✅ SUKSES! Service $SERVICE_NAME telah terpasang dan berjalan otomatis!"
echo ""
echo "Perintah berguna untuk mengelola bot di VPS:"
echo "  • Cek status bot : sudo systemctl status telegram-profile-rotator"
echo "  • Cek log live   : sudo journalctl -u telegram-profile-rotator -f"
echo "  • Restart bot    : sudo systemctl restart telegram-profile-rotator"
echo "  • Hentikan bot   : sudo systemctl stop telegram-profile-rotator"
echo "============================================="
