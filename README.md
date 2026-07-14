# Tomris Restoran Django uygulaması

Mevcut tasarım Django 5.2 tabanlı bir uygulamaya dönüştürülmüştür. Menü ürünleri SQLite veritabanından okunur ve Django admin panelinden yönetilir.

## Kurulum

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Bu bilgisayardaki hazır Anaconda kurulumu ile aynı komutlar şöyle çalıştırılabilir:

```powershell
D:\anaconda\python.exe manage.py migrate
D:\anaconda\python.exe manage.py createsuperuser
D:\anaconda\python.exe manage.py runserver
```

- Site: `http://127.0.0.1:8000/`
- Yönetim paneli: `http://127.0.0.1:8000/admin/`

## Ürün yönetimi

Yönetim panelindeki **Ürünler** bölümünden:

- ürün adı, açıklaması ve fiyatı değiştirilebilir;
- kategori seçilebilir;
- ürün yayına alınabilir veya gizlenebilir;
- kategori içindeki gösterim sırası düzenlenebilir.

İlk `migrate` işleminde mevcut 10 menü ürünü otomatik olarak eklenir.

## Yapı

- `tomris_site/`: Django proje ayarları ve ana URL yapılandırması
- `restaurant/`: ürün modeli, admin, view, testler ve migration'lar
- `restaurant/templates/restaurant/home.html`: ana sayfa şablonu
- `restaurant/static/restaurant/`: site CSS, JavaScript ve görselleri
- `db.sqlite3`: yerel veritabanı
- `source-design/`: zipten çıkarılan orijinal tasarım kaynakları

Kök dizindeki eski `index.html` ve `assets/` klasörü yalnız statik tasarım referansı olarak korunmuştur; Django uygulamasının gerçek çıktısı `restaurant` uygulamasındadır.

## Yayın notu

Canlı ortamda `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` ve `DJANGO_ALLOWED_HOSTS` ortam değişkenleri ayarlanmalıdır.
