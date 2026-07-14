#!/usr/bin/env bash
# CloudPanel kurulu sunucu icin Tomris ilk kurulumu - root olarak BIR KERE calistir.
# nginx / SSL / guvenlik duvarini CloudPanel yonetir; bu script onlara DOKUNMAZ.
# (Panelsiz ciplak Ubuntu icin setup.sh kullanilir.)
#
# On kosullar (bu scripti calistirmadan ONCE):
#   1) db.sqlite3 ve media/ bu bilgisayardan scp ile /var/www/tomris/ altina kopyalanmis olmali.
#   2) deploy/.env.production dosyasi /var/www/tomris/.env olarak yerlestirilip SECRET_KEY doldurulmus olmali.
set -euo pipefail

APP_DIR=/var/www/tomris
REPO_URL=https://github.com/halilkarkaya/TomrisRestaurant.git
DOMAIN=ayse.nedenkapatilsin.com.tr
PORT=2402

echo "==> Sistem paketleri (nginx/certbot/ufw YOK - onlar CloudPanel'in isi)"
apt update
apt install -y python3-venv python3-pip git

echo "==> Proje klasoru"
mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
    git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

if [ ! -f .env ]; then
    echo "HATA: $APP_DIR/.env bulunamadi." >&2
    echo "deploy/.env.production'i .env olarak kopyalayip SECRET_KEY'i doldurun." >&2
    exit 1
fi

if [ ! -f db.sqlite3 ]; then
    echo "UYARI: db.sqlite3 yok; bos veritabaniyla (sadece ornek urunlerle) devam edilir."
fi
mkdir -p media logs

echo "==> Sanal ortam ve bagimliliklar"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Migrasyon ve statik dosyalar"
python manage.py migrate
python manage.py collectstatic --noinput
deactivate

echo "==> Dosya sahipligi (gunicorn'un db ve media'ya yazabilmesi icin)"
chown -R www-data:www-data "$APP_DIR"

echo "==> systemd servisi"
cp deploy/tomris.service /etc/systemd/system/tomris.service
systemctl daemon-reload
systemctl enable --now tomris

echo ""
echo "Sunucu tarafi tamam: gunicorn 127.0.0.1:$PORT'de calisiyor."
echo "Servis durumu: systemctl status tomris"
echo ""
echo "Simdi CloudPanel panelinde (https://50.114.185.125:8443) su 3 adim kaldi:"
echo "  1) Add Site -> Create a Reverse Proxy: $DOMAIN, hedef http://127.0.0.1:$PORT"
echo "  2) Site -> Vhost Editor: location /media/ blogu ekle (alias $APP_DIR/media/),"
echo "     client_max_body_size 12M yap"
echo "  3) DNS yayilinca Site -> SSL/TLS -> New Let's Encrypt Certificate"
