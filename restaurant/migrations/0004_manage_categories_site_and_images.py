import django.db.models.deletion
from django.db import migrations, models


CATEGORIES = (
    ("soups", "Çorbalar", "Günlük sıcak", 10),
    ("mains", "Ana Yemekler", "Mutfağın seçkisi", 20),
    ("desserts", "Tatlılar", "Sofranın sonu", 30),
    ("drinks", "İçecekler", "Sofraya eşlik edenler", 40),
)

SAMPLE_IMAGES = {
    ("soups", 10): "products/mercimek-corbasi.jpg",
    ("soups", 20): "products/ezogelin-corbasi.jpg",
    ("mains", 10): "products/firin-makarna.jpg",
    ("mains", 20): "products/kremali-tavuklu-makarna.jpg",
    ("mains", 30): "products/pilav-ustu-kavurma.jpg",
    ("mains", 40): "products/etli-kuru-fasulye.jpg",
    ("desserts", 10): "products/firin-sutlac.jpg",
    ("desserts", 20): "products/cevizli-baklava.jpg",
    ("drinks", 10): "products/turk-cayi.jpg",
    ("drinks", 20): "products/ev-limonatasi.jpg",
}


def create_categories_and_connect_products(apps, schema_editor):
    MenuCategory = apps.get_model("restaurant", "MenuCategory")
    Product = apps.get_model("restaurant", "Product")
    SiteSettings = apps.get_model("restaurant", "SiteSettings")

    category_ids = {}
    for slug, name, eyebrow, sort_order in CATEGORIES:
        category = MenuCategory.objects.create(
            slug=slug,
            name=name,
            eyebrow=eyebrow,
            sort_order=sort_order,
            is_active=True,
        )
        category_ids[slug] = category.pk

    for product in Product.objects.all():
        legacy_category = product.category
        product.menu_category_id = category_ids[legacy_category]
        product.image = SAMPLE_IMAGES.get((legacy_category, product.sort_order), "")
        product.save(update_fields=("menu_category", "image"))

    SiteSettings.objects.get_or_create(pk=1)


def reverse_categories(apps, schema_editor):
    Product = apps.get_model("restaurant", "Product")
    for product in Product.objects.select_related("menu_category"):
        product.category = product.menu_category.slug
        product.save(update_fields=("category",))


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0003_product_details")]

    operations = [
        migrations.CreateModel(
            name="MenuCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, verbose_name="Kategori adı")),
                ("slug", models.SlugField(help_text="İnternet adresinde kullanılır. Örnek: corbalar", max_length=80, unique=True, verbose_name="Bağlantı adı")),
                ("eyebrow", models.CharField(blank=True, help_text="Örnek: Günlük sıcak", max_length=100, verbose_name="Kısa üst başlık")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Görünüm sırası")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="Menüde göster")),
            ],
            options={"verbose_name": "Menü kategorisi", "verbose_name_plural": "Menü kategorileri", "ordering": ("sort_order", "name")},
        ),
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("brand_name", models.CharField(default="Tomris", max_length=60, verbose_name="Marka adı")),
                ("brand_type", models.CharField(default="Restoran", max_length=60, verbose_name="Marka alt yazısı")),
                ("hero_image", models.ImageField(blank=True, help_text="Boş bırakırsanız mevcut Atatürk görseli kullanılır.", upload_to="site/", verbose_name="Ana sayfa görseli")),
                ("hero_eyebrow", models.CharField(default="Atamıza saygıyla", max_length=100, verbose_name="Ana görsel üst başlığı")),
                ("hero_title_first", models.CharField(default="Tomris", max_length=80, verbose_name="Ana başlık ilk satır")),
                ("hero_title_second", models.CharField(default="Restoran", max_length=80, verbose_name="Ana başlık ikinci satır")),
                ("hero_lead", models.CharField(default="Türk mutfağının tanıdık lezzetleri, aynı sofrada özenle buluşuyor.", max_length=240, verbose_name="Ana sayfa açıklaması")),
                ("story_kicker", models.CharField(default="Tomris'in sofrası", max_length=100, verbose_name="Hikâye üst başlığı")),
                ("story_title", models.CharField(default="Geçmişe saygı,\nsofrada özen.", max_length=180, verbose_name="Hikâye başlığı")),
                ("story_intro", models.TextField(default="Tomris, Türk mutfağının klasik lezzetlerini özenle hazırlanan tariflerle sofranıza taşır.", verbose_name="Hikâye giriş metni")),
                ("story_body", models.TextField(default="Çorbadan tatlıya her tabak, misafirlerimizin kendini evinde hissetmesi için aynı dikkatle hazırlanır. Sade sunum, tanıdık tat ve sıcak bir sofra kültürü bu mutfağın temelini oluşturur.", verbose_name="Hikâye açıklaması")),
                ("story_quote", models.CharField(default="Türk mutfağının zarafeti, aynı sofrada.", max_length=200, verbose_name="Hikâye sözü")),
                ("menu_kicker", models.CharField(default="Günün sofrası", max_length=100, verbose_name="Menü üst başlığı")),
                ("menu_title", models.CharField(default="Menümüz", max_length=100, verbose_name="Menü başlığı")),
                ("menu_summary", models.CharField(default="Klasik tarifler, yalın sunumlar ve sofranın tanıdık lezzetleri.", max_length=240, verbose_name="Menü açıklaması")),
                ("menu_note", models.CharField(default="Ürün içerikleri ve fiyatlar işletme tarafından güncellenebilir.", max_length=240, verbose_name="Menü alt notu")),
                ("contact_kicker", models.CharField(default="Bizi ziyaret edin", max_length=100, verbose_name="İletişim üst başlığı")),
                ("contact_title", models.CharField(default="Aynı sofrada\nbuluşalım.", max_length=180, verbose_name="İletişim başlığı")),
                ("contact_text", models.CharField(default="Denizli Merkezefendi'deki Tomris Restoran'a ulaşmak için haritayı kullanabilirsiniz.", max_length=240, verbose_name="İletişim açıklaması")),
                ("address_title", models.CharField(default="Sırakapılar, Mimar Sinan Cd. No:30", max_length=200, verbose_name="Adres ana satırı")),
                ("address_detail", models.CharField(default="20400 Merkezefendi / Denizli", max_length=200, verbose_name="Adres ikinci satırı")),
                ("map_link", models.URLField(default="https://www.google.com/maps/place//data=!4m2!3m1!1s0x14c73f5e8b37752b:0x70b0c9299378aaf4?sa=X&ved=1t:8290&ictx=111", max_length=600, verbose_name="Google Haritalar bağlantısı")),
                ("map_embed", models.URLField(default="https://www.google.com/maps?q=S%C4%B1rakap%C4%B1lar%2C%20Mimar%20Sinan%20Cd.%20No%3A30%2C%2020400%20Merkezefendi%2FDenizli&output=embed", max_length=600, verbose_name="Harita yerleştirme bağlantısı")),
                ("opening_hours", models.CharField(default="Her gün 11.00 – 23.00", max_length=120, verbose_name="Çalışma saatleri")),
                ("footer_text", models.CharField(default="Türk mutfağının zarafeti, aynı sofrada.", max_length=200, verbose_name="Alt bölüm yazısı")),
            ],
            options={"verbose_name": "Site ayarları", "verbose_name_plural": "Site ayarları"},
        ),
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(blank=True, help_text="Yatay veya kare, net bir yemek fotoğrafı yükleyin.", upload_to="products/", verbose_name="Ürün resmi"),
        ),
        migrations.AddField(
            model_name="product",
            name="menu_category",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products", to="restaurant.menucategory", verbose_name="Kategori"),
        ),
        migrations.RunPython(create_categories_and_connect_products, reverse_categories),
        migrations.RemoveIndex(model_name="product", name="product_menu_lookup"),
        migrations.RemoveField(model_name="product", name="category"),
        migrations.RenameField(model_name="product", old_name="menu_category", new_name="category"),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="restaurant.menucategory", verbose_name="Kategori"),
        ),
        migrations.AlterModelOptions(
            name="product",
            options={"ordering": ("category__sort_order", "sort_order", "name"), "verbose_name": "Ürün", "verbose_name_plural": "Ürünler"},
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["category", "is_active", "sort_order"], name="product_menu_lookup"),
        ),
    ]
