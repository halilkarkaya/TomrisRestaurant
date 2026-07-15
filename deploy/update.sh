#!/usr/bin/env bash
# Tomris Restoran'i main dalindan guvenli bicimde gunceller.
# Kullanim: sudo bash deploy/update.sh
# Testlerle: sudo RUN_TESTS=1 bash deploy/update.sh
set -Eeuo pipefail
umask 027

APP_DIR=/var/www/tomris
BRANCH=main
DOMAIN=tomrisrestoran.com.tr
PORT=8090
SERVICE=tomris
LOCK_FILE=/run/lock/tomris-update.lock
RUN_TESTS=${RUN_TESTS:-0}

fail() {
    echo "HATA: $*" >&2
    exit 1
}

if [ "${EUID}" -ne 0 ]; then
    fail "Bu betigi root olarak calistirin: sudo bash deploy/update.sh"
fi

command -v git >/dev/null 2>&1 || fail "git bulunamadi."
command -v python3 >/dev/null 2>&1 || fail "python3 bulunamadi."
command -v curl >/dev/null 2>&1 || fail "curl bulunamadi."
command -v flock >/dev/null 2>&1 || fail "flock bulunamadi."

[ -d "$APP_DIR/.git" ] || fail "$APP_DIR bir Git deposu degil."
[ -f "$APP_DIR/.env" ] || fail "$APP_DIR/.env bulunamadi."

exec 9>"$LOCK_FILE"
flock -n 9 || fail "Baska bir Tomris guncellemesi halen calisiyor."

cd "$APP_DIR"
GIT=(git -c "safe.directory=$APP_DIR" -C "$APP_DIR")

CURRENT_BRANCH=$("${GIT[@]}" branch --show-current)
[ "$CURRENT_BRANCH" = "$BRANCH" ] || fail "Sunucu $CURRENT_BRANCH dalinda; beklenen dal $BRANCH."

if ! "${GIT[@]}" diff --quiet || ! "${GIT[@]}" diff --cached --quiet; then
    fail "Sunucuda commitlenmemis takip edilen dosya degisiklikleri var. Once bunlari inceleyin."
fi

OLD_COMMIT=$("${GIT[@]}" rev-parse --short HEAD)

BACKUP_FILE=""
if [ -f "$APP_DIR/db.sqlite3" ]; then
    echo "==> Veritabani yedegi"
    install -d -m 700 "$APP_DIR/backups"
    BACKUP_FILE="$APP_DIR/backups/db-$(date +%Y%m%d-%H%M%S).sqlite3"
    python3 -c 'import sqlite3, sys; source = sqlite3.connect("file:" + sys.argv[1] + "?mode=ro", uri=True); target = sqlite3.connect(sys.argv[2]); source.backup(target); target.close(); source.close()' "$APP_DIR/db.sqlite3" "$BACKUP_FILE"
    chmod 600 "$BACKUP_FILE"
    echo "    $BACKUP_FILE"
fi

echo "==> Kod guncelleniyor ($BRANCH)"
"${GIT[@]}" fetch --prune origin "$BRANCH"
"${GIT[@]}" merge --ff-only "origin/$BRANCH"
NEW_COMMIT=$("${GIT[@]}" rev-parse --short HEAD)

if [ ! -x "$APP_DIR/venv/bin/python" ]; then
    echo "==> Sanal ortam olusturuluyor"
    python3 -m venv "$APP_DIR/venv"
fi

PYTHON="$APP_DIR/venv/bin/python"

echo "==> Bagimliliklar"
"$PYTHON" -m pip install --disable-pip-version-check -r "$APP_DIR/requirements.txt"

echo "==> Django kontrolleri"
"$PYTHON" manage.py check --deploy
if [ "$RUN_TESTS" = "1" ]; then
    echo "==> Django testleri"
    "$PYTHON" manage.py test --noinput
fi

echo "==> Migrasyonlar"
"$PYTHON" manage.py migrate --noinput

echo "==> Statik dosyalar"
"$PYTHON" manage.py collectstatic --noinput

echo "==> Yazilabilir klasor izinleri"
install -d -o www-data -g www-data "$APP_DIR/media" "$APP_DIR/logs"
if [ -f "$APP_DIR/db.sqlite3" ]; then
    chown www-data:www-data "$APP_DIR/db.sqlite3"
fi

if ! cmp -s "$APP_DIR/deploy/tomris.service" "/etc/systemd/system/tomris.service"; then
    echo "==> systemd servis tanimi guncelleniyor"
    install -m 644 "$APP_DIR/deploy/tomris.service" "/etc/systemd/system/tomris.service"
    systemctl daemon-reload
fi

echo "==> $SERVICE servisi yeniden baslatiliyor"
systemctl restart "$SERVICE"

echo "==> Saglik kontrolu"
HEALTHY=0
for _ in {1..15}; do
    if curl --fail --silent --max-time 5 \
        --header "Host: $DOMAIN" \
        --header "X-Forwarded-Proto: https" \
        --output /dev/null \
        "http://127.0.0.1:$PORT/"; then
        HEALTHY=1
        break
    fi
    sleep 1
done

if [ "$HEALTHY" -ne 1 ]; then
    systemctl status "$SERVICE" --no-pager || true
    journalctl -u "$SERVICE" -n 60 --no-pager || true
    fail "Uygulama 127.0.0.1:$PORT uzerinde saglik kontrolunu gecemedi."
fi

echo ""
echo "Guncelleme tamamlandi: $OLD_COMMIT -> $NEW_COMMIT"
[ -z "$BACKUP_FILE" ] || echo "Veritabani yedegi: $BACKUP_FILE"
echo "Canli adres: https://$DOMAIN"
