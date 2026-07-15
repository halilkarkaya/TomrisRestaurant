# Tomris Restoran — CloudPanel yayın kılavuzu

| Ayar | Değer |
|---|---|
| Ana adres | `https://tomrisrestoran.com.tr` |
| Yönlendirilecek adres | `https://www.tomrisrestoran.com.tr` |
| Sunucu | `166.1.94.195` |
| CloudPanel | `https://166.1.94.195:8443` |
| Uygulama klasörü | `/var/www/tomris` |
| Gunicorn | `127.0.0.1:8090` |
| systemd servisi | `tomris` |

## 1. DNS

Alan adı panelinde şu kayıtları oluşturun:

```text
@     A       166.1.94.195
www   CNAME   tomrisrestoran.com.tr
```

İki adres de `166.1.94.195` sonucunu vermeden SSL adımına geçmeyin:

```bash
dig +short tomrisrestoran.com.tr
dig +short www.tomrisrestoran.com.tr
```

## 2. Temiz sunucu kurulumu

CloudPanel sunucusuna root ile bağlanın. Eski `db.sqlite3` veya `media/` klasörünü
kopyalamayın; migration'lar temiz veritabanını örnek menü ürünleriyle oluşturur.

```bash
sudo mkdir -p /var/www
sudo git clone --branch main https://github.com/halilkarkaya/TomrisRestaurant.git /var/www/tomris
cd /var/www/tomris
sudo bash deploy/setup-cloudpanel.sh
```

Betik güçlü bir `DJANGO_SECRET_KEY` üretir, bağımlılıkları kurar, Django üretim
kontrollerini çalıştırır, migration ve `collectstatic` işlemlerini tamamlar, yönetici
hesabını sorar ve `tomris` servisini başlatır. 8090 portu doluysa mevcut sürece
dokunmadan durur.

## 3. CloudPanel

1. **Add Site → Create a Reverse Proxy** ile `tomrisrestoran.com.tr` sitesini ve
   `http://127.0.0.1:8090` hedefini oluşturun.
2. Siteye `www.tomrisrestoran.com.tr` alan adını ekleyin.
3. **Vhost Editor** içinde [cloudpanel-vhost-snippet.conf](cloudpanel-vhost-snippet.conf)
   içeriğini HTTPS `server` bloğuna ekleyin ve yapılandırmayı doğrulayın.
4. DNS yayıldıktan sonra iki alan adını da kapsayan Let's Encrypt sertifikası oluşturun.

Snippet; `www` adresini ana HTTPS adrese yönlendirir, yükleme sınırını 12 MB yapar ve
`/media/` dosyalarına bir yıllık immutable tarayıcı önbelleği uygular.

## 4. Doğrulama

```bash
systemctl status tomris --no-pager
journalctl -u tomris -n 100 --no-pager
curl -I http://127.0.0.1:8090/ -H 'Host: tomrisrestoran.com.tr'
curl -I https://tomrisrestoran.com.tr/
curl -I https://www.tomrisrestoran.com.tr/
```

Beklenen davranış: ana adres `200`, HTTP ve `www` tek adımda
`https://tomrisrestoran.com.tr` adresine `301` döndürür. `/admin/`, statik dosyalar ve
yeni yüklenen ürün görselleri ayrıca kontrol edilmelidir.

## Sonraki güncellemeler

Kod `main` dalına gönderildikten sonra sunucuda:

```bash
cd /var/www/tomris
sudo bash deploy/deploy.sh
```

Güncelleme betiği veritabanını ve media dosyalarını silmez.
