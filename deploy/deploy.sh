#!/usr/bin/env bash
# Sonraki guncellemeler icin: yeni kod GitHub'a push edildikten sonra sunucuda root/sudo ile calistir.
set -euo pipefail

APP_DIR=/var/www/tomris
cd "$APP_DIR"

echo "==> Kod guncelleniyor"
sudo -u www-data git pull

source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
deactivate

echo "==> Servis yeniden baslatiliyor"
systemctl restart tomris

echo "Guncelleme tamamlandi."
