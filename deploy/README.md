# Tomris Restoran — Yayın (Deploy) Kılavuzu

Site, mevcut **nedenkapatilsin.com.tr** sunucusuna **ikinci uygulama** olarak,
`ayse.nedenkapatilsin.com.tr` alt alan adıyla kurulur. Nedenkapatilsin'e dokunulmaz.

| Ayar | Değer |
|------|-------|
| Alan adı | `ayse.nedenkapatilsin.com.tr` |
| Uygulama klasörü | `/var/www/tomris` |
| Gunicorn portu | `127.0.0.1:2402` |
| systemd servisi | `tomris` |
| nginx site | `/etc/nginx/sites-available/tomris` |

nedenkapatilsin `8090` portunu ve `nedenkapatilsin` servisini kullanır; Tomris `2402`
portunu ve `tomris` servisini kullanır. Çakışma yoktur.

---

## 1. Bu bilgisayarda: kodu GitHub'a yükle ✅ (yapıldı)

Kod şu depoya gönderildi: **https://github.com/halilkarkaya/TomrisRestaurant**
(`db.sqlite3` ve `.env` `.gitignore` sayesinde **gönderilmedi** — veriyi 3. adımda
`scp` ile ayrıca taşıyacağız). Sonraki güncellemeleri `git push` ile gönderin.

## 2. DNS: alt alan adını sunucuya yönlendir

Alan adı yönetim panelinizde (nedenkapatilsin.com.tr'nin DNS'i) bir **A kaydı** ekleyin:

```
Tip: A    Ad: ayse    Değer: <SUNUCU_IP>
```

Yayılmayı doğrulayın (sunucunun IP'sini göstermeli):

```bash
dig +short ayse.nedenkapatilsin.com.tr
```

## 3. Sunucuda: klonla, veriyi taşı, .env yerleştir

```bash
# Sunucuda (root/sudo):
sudo mkdir -p /var/www/tomris
sudo git clone https://github.com/halilkarkaya/TomrisRestaurant.git /var/www/tomris
```

Bu bilgisayardan **canlı veriyi** ve **görselleri** sunucuya kopyalayın
(proje klasöründen çalıştırın):

```powershell
scp db.sqlite3 <KULLANICI>@<SUNUCU_IP>:/var/www/tomris/
scp -r media    <KULLANICI>@<SUNUCU_IP>:/var/www/tomris/
```

`.env` dosyasını hazırlayıp yerleştirin:

```bash
# Sunucuda:
cd /var/www/tomris
sudo cp deploy/.env.production .env
# SECRET_KEY üretin ve .env içine yazın:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
sudo nano .env      # DJANGO_SECRET_KEY satırını doldurun
```

## 4. Sunucuda: kurulumu çalıştır

```bash
cd /var/www/tomris
sudo bash deploy/setup.sh
```

Script; sanal ortamı kurar, bağımlılıkları yükler, `migrate` + `collectstatic`
çalıştırır, dosya sahipliğini `www-data`'ya verir, `tomris` servisini ve nginx
bloğunu ekler, ardından `certbot` ile SSL sertifikası alır.

Certbot "HTTP'yi HTTPS'e yönlendir" sorusuna **Redirect (2)** yanıtı verin.

## 5. Yayın sonrası

- **Site:** https://ayse.nedenkapatilsin.com.tr
- **Yönetim:** https://ayse.nedenkapatilsin.com.tr/admin/
- Servis durumu: `systemctl status tomris`
- Loglar: `journalctl -u tomris -f`

### Önemli: admin şifresini güçlendirin
Canlı veritabanı `tomris` admin hesabını taşıyor ve mevcut şifresi zayıf.
Yayına aldıktan sonra admin panelinden **güçlü bir şifreyle** değiştirin
(sağ üst → şifre değiştir), ya da sunucuda:

```bash
cd /var/www/tomris && source venv/bin/activate
python manage.py changepassword tomris
```

### HSTS'i açın (isteğe bağlı, site HTTPS'te sorunsuz çalıştıktan sonra)
`.env` içinde `DJANGO_SECURE_HSTS_SECONDS=31536000` yapıp `sudo systemctl restart tomris`.

---

## Sonraki güncellemeler

Kodda değişiklik yapıp GitHub'a push ettikten sonra, sunucuda:

```bash
cd /var/www/tomris && sudo bash deploy/deploy.sh
```

> Not: `deploy.sh` kodu `git pull` ile günceller; `db.sqlite3` sunucuda kalır
> (git'e dahil değildir), böylece canlı içerik korunur.
