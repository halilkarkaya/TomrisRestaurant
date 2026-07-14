#!/usr/bin/env bash
# Tomris ilk kurulum scripti - mevcut nedenkapatilsin sunucusunda root/sudo ile BIR KERE calistir.
#
# On kosullar (bu scripti calistirmadan ONCE):
#   1) DNS: ayse.nedenkapatilsin.com.tr icin A kaydi bu sunucunun IP'sine yayilmis olmali.
#   2) Kod: /var/www/tomris klasorune depo git clone edilmis olmali.
#   3) Veri: db.sqlite3 ve media/ bu bilgisayardan scp ile /var/www/tomris/ altina kopyalanmis olmali.
#   4) Ayar: deploy/.env.production dosyasi /var/www/tomris/.env olarak yerlestirilmis olmali.
# Ayrinti icin deploy/README.md dosyasina bakin.
set -euo pipefail

APP_DIR=/var/www/tomris
REPO_URL=https://github.com/halilkarkaya/tomris.git   # <-- kendi depo adresinizle guncelleyin
DOMAIN=ayse.nedenkapatilsin.com.tr

echo "==> Proje klasoru"
mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
    git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

if [ ! -f .env ]; then
    echo "HATA: $APP_DIR/.env bulunamadi." >&2
    echo "Once deploy/.env.production dosyasini $APP_DIR/.env olarak kopyalayip SECRET_KEY'i doldurun." >&2
    exit 1
fi

if [ ! -f db.sqlite3 ]; then
    echo "UYARI: db.sqlite3 yok. Mevcut icerigi tasimak icin once scp ile kopyalayin;"
    echo "       aksi halde bos veritabaniyla (sadece ornek urunlerle) devam edilir."
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

echo "==> nginx (yalnizca bu site eklenir; nedenkapatilsin'e dokunulmaz)"
cp deploy/nginx.conf /etc/nginx/sites-available/tomris
ln -sf /etc/nginx/sites-available/tomris /etc/nginx/sites-enabled/tomris
nginx -t
systemctl reload nginx

echo "==> SSL sertifikasi (DNS bu sunucuya yayilmis olmali)"
certbot --nginx -d "$DOMAIN"

echo ""
echo "Kurulum tamamlandi: https://$DOMAIN"
echo "Servis durumu: systemctl status tomris"
echo "Loglar:        journalctl -u tomris -f"
