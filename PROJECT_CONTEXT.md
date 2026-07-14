# Tomris Restoran — Proje Bağlamı

Bu belge, projeyi ilk kez açan bir geliştiricinin veya yapay zekâ ajanının uygulamanın ne yaptığını, bir isteğin hangi dosyalardan geçtiğini ve değişikliklerin nerede yapılması gerektiğini hızlıca anlaması için hazırlanmıştır.

## 1. Projenin amacı

Bu proje, **Tomris Restoran** için hazırlanmış Django tabanlı bir tanıtım ve dijital menü sitesidir.

Ziyaretçi tarafında:

- restoranın ana tanıtım alanı gösterilir;
- restoran hikâyesi ve marka metinleri sunulur;
- aktif menü kategorileri ve ürünler listelenir;
- her ürünün ayrı detay sayfası vardır;
- ürün resmi, açıklaması, fiyatı, içindekiler ve alerjen bilgisi gösterilir;
- adres, çalışma saatleri ve Google Haritalar bağlantısı sunulur.

Yönetici tarafında `/admin/` üzerinden:

- ürün eklenebilir, düzenlenebilir, sıralanabilir, yayına alınabilir veya gizlenebilir;
- ürün resmi, fiyatı, açıklaması, içindekiler ve alerjen bilgisi yönetilebilir;
- menü kategorileri ve sıraları yönetilebilir;
- ana sayfadaki marka, hikâye, menü, iletişim ve harita metinleri değiştirilebilir.

## 2. Kullanılan teknoloji

| Katman | Teknoloji |
| --- | --- |
| Backend | Python, Django 5.2.8 |
| Veritabanı | SQLite (`db.sqlite3`) |
| Görsel işleme | Pillow 10.3.0 |
| Şablon | Django Template Language |
| Stil | Saf CSS |
| Etkileşim | Saf JavaScript |
| Yönetim | Özelleştirilmiş Django Admin |

Harici bir frontend framework, REST API veya SPA katmanı yoktur. Sayfalar sunucu tarafında HTML olarak oluşturulur.

## 3. Kaynakların doğruluk sırası

Aktif çalışan Django uygulamasında düzenleme yaparken şu dosyalar kaynak kabul edilmelidir:

1. `restaurant/templates/restaurant/`
2. `restaurant/static/restaurant/`
3. `restaurant/models.py`, `views.py`, `urls.py`, `admin.py`
4. `tomris_site/settings.py` ve `tomris_site/urls.py`

Şu yollar çalışan sitenin kaynağı **değildir**:

- kökteki `index.html` ve `assets/`: eski statik tasarım referansı;
- `source-design/`: ilk tasarım/prototip kaynakları;
- `staticfiles/`: `collectstatic` tarafından üretilen çıktı, doğrudan düzenlenmemeli;
- `Tomris Restoran Web Sitesi.zip`: arşiv/kopya;
- `db.sqlite3`: yerel çalışma verisi, kod değildir.

Önemli: Görsel veya CSS değişikliği yapılacaksa `restaurant/static/restaurant/` altı düzenlenir. `staticfiles/` elle değiştirilmez.

## 4. İstek akışı — ne nereye gidiyor?

```text
Tarayıcı isteği
    |
    v
tomris_site/urls.py
    |
    +-- /admin/ ----------------------> Django Admin
    |
    +-- diğer adresler --------------> restaurant/urls.py
                                          |
                     +--------------------+--------------------+
                     |                                         |
                     v                                         v
              views.home()                         views.product_detail()
                     |                                         |
                     v                                         v
     MenuCategory + Product + SiteSettings       Product + SiteSettings
                     |                                         |
                     v                                         v
        restaurant/home.html              restaurant/product_detail.html
                     |                                         |
                     +--------------------+--------------------+
                                          |
                                          v
                         CSS + JS + statik/medya görselleri
                                          |
                                          v
                                      HTML yanıtı
```

### Ana sayfa isteği

`GET /` isteği `restaurant.views.home` fonksiyonuna gider.

Bu view:

1. yalnızca `is_active=True` ürünleri alır;
2. ürünleri `sort_order`, ardından `name` ile sıralar;
3. yalnızca aktif kategorileri alır;
4. ürünleri kategorilere `prefetch_related` ile bağlar;
5. tekil `SiteSettings` kaydını yükler;
6. veriyi `restaurant/home.html` şablonuna gönderir.

Şablona gönderilen ana context:

```python
{
    "categories": categories,
    "site": SiteSettings.load(),
}
```

### Ürün detay isteği

`GET /urun/<id>/<slug>/` isteği `restaurant.views.product_detail` fonksiyonuna gider.

Bu view:

1. ürünü kategorisiyle birlikte getirir;
2. hem ürünün hem kategorinin aktif olmasını şart koşar;
3. ürün bulunamazsa 404 döndürür;
4. URL slug'ı ürün adından üretilen güncel slug değilse kalıcı yönlendirme yapar;
5. ürünü ve site ayarlarını `restaurant/product_detail.html` şablonuna gönderir.

## 5. URL haritası

| URL | İsim | View / hedef | Amaç |
| --- | --- | --- | --- |
| `/` | `restaurant:home` | `restaurant.views.home` | Ana sayfa ve menü |
| `/urun/<pk>/<slug>/` | `restaurant:product_detail` | `restaurant.views.product_detail` | Ürün detay sayfası |
| `/admin/` | Django Admin | `admin.site.urls` | İçerik yönetimi |
| `/media/...` | Yalnız `DEBUG=True` iken Django | `MEDIA_ROOT` | Yüklenen görseller |
| `/static/...` | Django staticfiles | Uygulama statikleri | CSS, JS ve sabit görseller |

## 6. Veri modeli

### `MenuCategory`

Menüdeki kategori başlıklarını temsil eder.

Önemli alanlar:

- `name`: görünen kategori adı;
- `slug`: sayfa içi bağlantı/kimlik;
- `eyebrow`: kategori yanındaki kısa üst başlık;
- `sort_order`: menü sırası;
- `is_active`: kategorinin sitede gösterilip gösterilmediği.

Kategori silme sırasında ürün ilişkisi `PROTECT` ile korunur. Ürün taşıyan bir kategori doğrudan silinemez.

### `Product`

Restoran menüsündeki ürünü temsil eder.

Önemli alanlar:

- `name`;
- `category` → `MenuCategory`;
- `image` → `media/products/`;
- `description`;
- `ingredients`;
- `allergen_info`;
- `price`;
- `sort_order`;
- `is_active`;
- `created_at`, `updated_at`.

`get_absolute_url()` Türkçe karakterleri normalize eden `turkish_slugify()` ile ürün detay URL'sini oluşturur. Ürün adının değişmesi slug'ı da değiştirir; eski slug'a gelen istek güncel URL'ye 301 yönlendirilir.

### `SiteSettings`

Ana sayfadaki düzenlenebilir metinleri, ana görseli, adresi, haritayı ve çalışma saatlerini tutan **tekil kayıt** modelidir.

- Her zaman `pk=1` kullanır.
- `SiteSettings.load()` kayıt yoksa otomatik oluşturur.
- Admin yeni ikinci kayıt oluşturulmasına ve kaydın silinmesine izin vermez.

Ana alan grupları:

- marka ve hero;
- hikâye/hakkımızda;
- menü başlıkları ve notu;
- iletişim, adres, çalışma saatleri ve harita;
- footer metni.

## 7. Admin paneli

Admin arayüzü standart Django Admin üzerine özel şablon ve CSS eklenerek hazırlanmıştır.

İlgili dosyalar:

- `restaurant/admin.py`: formlar, liste ekranları, sıralama ve toplu işlemler;
- `templates/admin/base_site.html`: yönetim paneli üst alanı;
- `templates/admin/index.html`: özel yönetim ana sayfası ve hızlı işlemler;
- `restaurant/static/restaurant/css/admin.css`: admin görünümü.

Ürün sıralaması admin formunda kullanıcıya normal sıra numarası olarak gösterilir. Kaydederken `sort_order` değerleri 10, 20, 30... biçiminde yeniden dağıtılır. Kategori değiştirilen ürün için hem eski hem yeni kategori yeniden sıralanır.

Admin toplu ürün işlemleri:

- seçilen ürünleri menüde göster;
- seçilen ürünleri menüden gizle.

## 8. Frontend yapısı

### Şablonlar

- `restaurant/templates/restaurant/home.html`: header, hero, hikâye, menü, iletişim ve footer;
- `restaurant/templates/restaurant/product_detail.html`: ürün resmi, açıklama, fiyat, içerik ve alerjen bilgisi.

### CSS

- `restaurant/static/restaurant/css/styles.css`: ziyaretçi sitesinin tüm responsive tasarımı;
- `restaurant/static/restaurant/css/admin.css`: yalnızca admin paneli.

Tasarım dili koyu ceviz/siyah zemin, pirinç-altın vurgular, Bodoni Moda başlık fontu ve Alegreya Sans gövde fontu üzerine kuruludur.

Menü ürünleri iki sütunlu kategori düzeninde gösterilir. Ürün resmi varsa `menu-item__link--with-image` sınıfı eklenir ve resim ürün metninin yanında küçük 4:3 görsel olarak yer alır. Mobil görünümde kategori listesi tek sütuna düşer ve ürün resmi daha küçük kalır.

### JavaScript

`restaurant/static/restaurant/js/main.js` şunları yönetir:

- mobil menünün açılıp kapanması;
- Escape ve Tab ile klavye erişilebilirliği;
- scroll durumunda header görünümü;
- görünür bölüme göre aktif navigasyon bağlantısı;
- hash bağlantısından sonra odağın doğru bölüme taşınması;
- Türk bayrağı görseli yüklenemezse fallback davranışı;
- footer yılının otomatik güncellenmesi.

## 9. Statik ve medya dosyaları

### Statik dosyalar

Kaynak dizin:

```text
restaurant/static/restaurant/
├── css/
├── images/
└── js/
```

Canlı dağıtım öncesinde:

```powershell
D:\anaconda\python.exe manage.py collectstatic --noinput
```

Bu komut çıktıyı `staticfiles/` dizinine toplar.

### Kullanıcı/yönetici tarafından yüklenen görseller

```text
media/
├── products/   # Ürün resimleri
└── site/       # Admin üzerinden yüklenirse ana sayfa görseli
```

`DEBUG=True` iken medya URL'leri Django tarafından servis edilir. Canlı ortamda medya dosyalarının web sunucusu veya uygun bir depolama servisi tarafından sunulması gerekir.

## 10. Kurulum ve çalıştırma

```powershell
D:\anaconda\python.exe -m pip install -r requirements.txt
D:\anaconda\python.exe manage.py migrate
D:\anaconda\python.exe manage.py createsuperuser
D:\anaconda\python.exe manage.py runserver
```

Yerel adresler:

- Site: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

İlk migration zinciri örnek kategorileri, 10 örnek ürünü, ürün görsellerinin yollarını ve tekil site ayarı kaydını oluşturur.

## 11. Test ve doğrulama

Kod değişikliğinden sonra en az şu komutlar çalıştırılmalıdır:

```powershell
D:\anaconda\python.exe manage.py check
D:\anaconda\python.exe manage.py test
```

Testler şu davranışları kapsar:

- aktif ürünlerin ana sayfada gösterilmesi;
- kategori bağlantıları;
- site ayarlarının sayfaya yansıması;
- adres ve harita;
- ürün detay bağlantısı ve detay sayfası;
- gizli ürünün 404 vermesi;
- admin sayfalarının ve yönetim alanlarının erişilebilirliği;
- kategori, ürün ve site ayarı yönetimi.

Görsel değişikliklerde ayrıca masaüstü ve mobil viewport ile gerçek tarayıcı kontrolü yapılmalıdır.

## 12. Ortam değişkenleri ve yayın

| Değişken | Yerel varsayılan | Canlı ortam |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Güvensiz geliştirme anahtarı | Zorunlu, gizli değer verilmeli |
| `DJANGO_DEBUG` | `1` | `0` olmalı |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost,testserver` | Gerçek alan adları verilmeli |

Mevcut proje yerelde SQLite kullanır. Üretim trafiği artarsa PostgreSQL'e geçiş, kalıcı medya depolaması, HTTPS/proxy ayarları ve production WSGI/ASGI sunucusu ayrıca yapılandırılmalıdır. Django geliştirme sunucusu canlı ortam için kullanılmamalıdır.

## 13. Sık değişikliklerde hangi dosya?

| İstenen değişiklik | Öncelikli dosya |
| --- | --- |
| Ana sayfa HTML yapısı | `restaurant/templates/restaurant/home.html` |
| Ürün detay HTML yapısı | `restaurant/templates/restaurant/product_detail.html` |
| Site görünümü, boyutlar, responsive tasarım | `restaurant/static/restaurant/css/styles.css` |
| Mobil menü ve scroll davranışı | `restaurant/static/restaurant/js/main.js` |
| Ürün/kategori/site alanları | `restaurant/models.py` + yeni migration |
| Ana sayfaya gönderilen veri | `restaurant/views.py` |
| Yeni sayfa veya URL | `restaurant/urls.py` ve gerekirse `tomris_site/urls.py` |
| Admin formu/liste/sıralama | `restaurant/admin.py` |
| Admin görünümü | `templates/admin/` ve `restaurant/static/restaurant/css/admin.css` |
| Genel Django ayarları | `tomris_site/settings.py` |

## 14. Değişiklik yaparken korunması gereken kurallar

1. Gizli ürün veya gizli kategori ziyaretçi sayfalarında gösterilmemeli.
2. `SiteSettings` tekil kayıt olarak kalmalı.
3. Model değişikliği migration olmadan bırakılmamalı.
4. Ürün URL'lerinde `get_absolute_url()` kullanılmalı; slug elle oluşturulmamalı.
5. `staticfiles/`, `source-design/`, kök `index.html` veya `assets/` aktif uygulama sanılarak düzenlenmemeli.
6. Ürün resimleri farklı oranlarda gelebileceği için CSS'te `object-fit: cover` ve kontrollü `aspect-ratio` korunmalı.
7. Yeni frontend davranışlarında klavye odağı, mobil görünüm ve `prefers-reduced-motion` dikkate alınmalı.
8. Kullanıcı tarafından yapılmış ilgisiz değişiklikler geri alınmamalı.

## 15. Yeni bir yapay zekâ ajanı için başlangıç kontrol listesi

1. Bu dosyayı ve varsa kökteki `AGENTS.md` talimatlarını oku.
2. Görevin hangi katmana ait olduğunu belirle.
3. Kod keşfinde önce codebase knowledge graph araçlarını kullan.
4. Aktif kaynak ile eski prototip klasörlerini karıştırma.
5. İlgili model/view/template/CSS akışını birlikte kontrol et.
6. Değişiklikten sonra `manage.py check` ve ilgili testleri çalıştır.
7. Görsel değişiklikte en az masaüstü ve mobil görünümü doğrula.

