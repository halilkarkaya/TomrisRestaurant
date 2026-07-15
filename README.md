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

Yüklenen ürün fotoğrafları kayıt sırasında WebP biçimine dönüştürülür; ana dosya en
fazla 1200 piksel genişlikte, uygun görseller için 480 ve 960 piksel responsive
varyantlarla saklanır. Ana sayfa görseli en fazla 1920 piksele küçültülür.

## İletişim ve sosyal medya

Yönetim panelindeki **Site ayarları** bölümünden:

- telefon numarası girildiğinde iletişim bölümünde tıklanabilir olarak görünür;
- WhatsApp numarası girildiğinde hem "WhatsApp'tan yazın" butonu hem de
  sağ altta sabit bir WhatsApp simgesi eklenir;
- Instagram ve Facebook bağlantıları alt bölümde ikon olarak görünür.

Bu alanlar boş bırakıldığında sitede hiçbir ilgili öğe gösterilmez.

## Yapı

- `tomris_site/`: Django proje ayarları ve ana URL yapılandırması
- `restaurant/`: ürün modeli, admin, view, testler ve migration'lar
- `restaurant/templates/restaurant/base.html`: ortak sayfa iskeleti (head, header, footer)
- `restaurant/templates/restaurant/home.html` ve `product_detail.html`: `base.html`'i genişleten sayfalar
- `restaurant/static/restaurant/fonts/`: yerel barındırılan yazı tipleri (Bodoni Moda, Alegreya Sans)
- `restaurant/static/restaurant/`: site CSS, JavaScript ve görselleri
- `templates/404.html` ve `templates/500.html`: özel hata sayfaları
- `db.sqlite3`: yerel veritabanı
- `source-design/`: zipten çıkarılan orijinal tasarım kaynakları

Yazı tipleri Google Fonts CDN yerine yerelden yüklenir; bu sayede sayfa daha
hızlı açılır, çevrimdışı çalışır ve ziyaretçi verisi üçüncü tarafa gitmez.

Kök dizindeki eski `index.html` ve `assets/` klasörü yalnız statik tasarım referansı olarak korunmuştur; Django uygulamasının gerçek çıktısı `restaurant` uygulamasındadır.

## Yayın notu

Canlı ortamda aşağıdaki ortam değişkenleri ayarlanmalıdır:

- `DJANGO_SECRET_KEY`: rastgele, gizli bir anahtar
- `DJANGO_DEBUG=0`: hata ayıklamayı kapatır
- `DJANGO_ALLOWED_HOSTS`: alan adları (virgülle ayrılmış)

`DJANGO_DEBUG=0` iken güvenli çerezler, HTTPS yönlendirmesi ve statik dosya
sıkıştırması (WhiteNoise) otomatik olarak devreye girer. İsteğe bağlı:
`DJANGO_SECURE_HSTS_SECONDS` (HSTS süresi), `DJANGO_SECURE_SSL_REDIRECT`
(varsayılan açık) ve ters proxy arkasında `DJANGO_BEHIND_PROXY=1`.

Yayın öncesi statik dosyaları toplayın:

```powershell
python manage.py collectstatic --noinput
```
