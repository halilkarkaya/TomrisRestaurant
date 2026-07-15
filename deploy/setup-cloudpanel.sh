#!/usr/bin/env bash
# Tomris Restoran'i CloudPanel sunucusuna temiz veritabaniyla ilk kez kurar.
# CloudPanel nginx, alan adi ve SSL'i yonetir; bu betik uygulamayi ve systemd servisini kurar.
set -euo pipefail

APP_DIR=/var/www/tomris
REPO_URL=https://github.com/halilkarkaya/TomrisRestaurant.git
DOMAIN=tomrisrestoran.com.tr
WWW_DOMAIN=www.tomrisrestoran.com.tr
SERVER_IP=166.1.94.195
PORT=8090

if [ "${EUID}" -ne 0 ]; then
    echo "HATA: Bu betigi root olarak calistirin." >&2
    exit 1
fi

echo "==> Sistem paketleri"
apt update
apt install -y python3-venv python3-pip git curl

if ss -H -ltn "sport = :$PORT" | grep -q .; then
    echo "HATA: 127.0.0.1:$PORT portu kullanimda. Mevcut surece dokunulmadi." >&2
    exit 1
fi

echo "==> Proje"
mkdir -p "$(dirname "$APP_DIR")"
if [ ! -d "$APP_DIR/.git" ]; then
    git clone --branch main "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

if [ ! -f .env ]; then
    cp deploy/.env.production .env
    SECRET_VALUE=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
    sed -i "s|BURAYA-UZUN-RASTGELE-BIR-DEGER-YAZIN|$SECRET_VALUE|" .env
    chmod 600 .env
fi

if grep -q "BURAYA-UZUN-RASTGELE-BIR-DEGER-YAZIN" .env; then
    echo "HATA: .env icindeki DJANGO_SECRET_KEY guvenli bir degerle degistirilmemis." >&2
    exit 1
fi

if [ -f db.sqlite3 ]; then
    echo "UYARI: db.sqlite3 zaten var; veri kaybini onlemek icin mevcut dosya korunacak."
else
    echo "==> Temiz veritabani ornek menu verileriyle olusturulacak"
fi
mkdir -p media logs

echo "==> Sanal ortam ve bagimliliklar"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Django kontrolleri, migrasyon ve statik dosyalar"
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput

if ! python manage.py shell -c "from django.contrib.auth import get_user_model; raise SystemExit(0 if get_user_model().objects.filter(is_superuser=True).exists() else 1)"; then
    if [ -t 0 ]; then
        echo "==> Yonetici hesabi"
        python manage.py createsuperuser
    else
        echo "UYARI: Yonetici hesabi olusturulmadi. Daha sonra su komutu calistirin:"
        echo "  cd $APP_DIR && source venv/bin/activate && python manage.py createsuperuser"
    fi
fi
deactivate

echo "==> Dosya sahipligi ve systemd servisi"
chown -R www-data:www-data "$APP_DIR"
cp deploy/tomris.service /etc/systemd/system/tomris.service
systemctl daemon-reload
systemctl enable --now tomris

sleep 2
curl --fail --silent --show-error \
    --header "Host: $DOMAIN" \
    --header "X-Forwarded-Proto: https" \
    --output /dev/null \
    "http://127.0.0.1:$PORT/"

echo ""
echo "Uygulama hazir: http://127.0.0.1:$PORT"
echo "CloudPanel: https://$SERVER_IP:8443"
echo "1) Reverse Proxy sitesi: $DOMAIN -> http://127.0.0.1:$PORT"
echo "2) Alan adi olarak $WWW_DOMAIN adresini ekleyin."
echo "3) deploy/cloudpanel-vhost-snippet.conf icerigini Vhost Editor'a ekleyin."
echo "4) DNS yayilinca iki alan adini kapsayan Let's Encrypt sertifikasi olusturun."
