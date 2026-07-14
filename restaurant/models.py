from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


TURKISH_SLUG_TRANSLATION = str.maketrans(
    {
        "ç": "c",
        "Ç": "C",
        "ğ": "g",
        "Ğ": "G",
        "ı": "i",
        "İ": "I",
        "ö": "o",
        "Ö": "O",
        "ş": "s",
        "Ş": "S",
        "ü": "u",
        "Ü": "U",
    }
)


def turkish_slugify(value):
    return slugify(value.translate(TURKISH_SLUG_TRANSLATION))


class MenuCategory(models.Model):
    name = models.CharField("Kategori adı", max_length=80)
    slug = models.SlugField(
        "Bağlantı adı",
        max_length=80,
        unique=True,
        help_text="İnternet adresinde kullanılır. Örnek: corbalar",
    )
    eyebrow = models.CharField(
        "Kısa üst başlık",
        max_length=100,
        blank=True,
        help_text="Örnek: Günlük sıcak",
    )
    sort_order = models.PositiveIntegerField("Görünüm sırası", default=0)
    is_active = models.BooleanField("Menüde göster", default=True, db_index=True)

    class Meta:
        verbose_name = "Menü kategorisi"
        verbose_name_plural = "Menü kategorileri"
        ordering = ("sort_order", "name")

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Ürün adı", max_length=120)
    category = models.ForeignKey(
        MenuCategory,
        verbose_name="Kategori",
        related_name="products",
        on_delete=models.PROTECT,
    )
    image = models.ImageField(
        "Ürün resmi",
        upload_to="products/",
        blank=True,
        help_text="Yatay veya kare, net bir yemek fotoğrafı yükleyin.",
    )
    description = models.CharField("Açıklama", max_length=240, blank=True)
    ingredients = models.TextField("İçindekiler", blank=True)
    allergen_info = models.CharField("Alerjen bilgisi", max_length=200, blank=True)
    price = models.DecimalField(
        "Fiyat",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    sort_order = models.PositiveIntegerField("Sıra", default=0)
    is_active = models.BooleanField("Yayında", default=True, db_index=True)
    created_at = models.DateTimeField("Oluşturulma", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme", auto_now=True)

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ("category__sort_order", "sort_order", "name")
        indexes = [
            models.Index(
                fields=("category", "is_active", "sort_order"),
                name="product_menu_lookup",
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "restaurant:product_detail",
            kwargs={"pk": self.pk, "slug": turkish_slugify(self.name)},
        )


class SiteSettings(models.Model):
    brand_name = models.CharField("Marka adı", max_length=60, default="Tomris")
    brand_type = models.CharField("Marka alt yazısı", max_length=60, default="Restoran")
    hero_image = models.ImageField(
        "Ana sayfa görseli",
        upload_to="site/",
        blank=True,
        help_text="Boş bırakırsanız mevcut Atatürk görseli kullanılır.",
    )
    hero_eyebrow = models.CharField(
        "Ana görsel üst başlığı", max_length=100, default="Atamıza saygıyla"
    )
    hero_title_first = models.CharField("Ana başlık ilk satır", max_length=80, default="Tomris")
    hero_title_second = models.CharField(
        "Ana başlık ikinci satır", max_length=80, default="Restoran"
    )
    hero_lead = models.CharField(
        "Ana sayfa açıklaması",
        max_length=240,
        default="Türk mutfağının tanıdık lezzetleri, aynı sofrada özenle buluşuyor.",
    )
    story_kicker = models.CharField("Hikâye üst başlığı", max_length=100, default="Tomris'in sofrası")
    story_title = models.CharField(
        "Hikâye başlığı", max_length=180, default="Geçmişe saygı,\nsofrada özen."
    )
    story_intro = models.TextField(
        "Hikâye giriş metni",
        default="Tomris, Türk mutfağının klasik lezzetlerini özenle hazırlanan tariflerle sofranıza taşır.",
    )
    story_body = models.TextField(
        "Hikâye açıklaması",
        default=(
            "Çorbadan tatlıya her tabak, misafirlerimizin kendini evinde hissetmesi için "
            "aynı dikkatle hazırlanır. Sade sunum, tanıdık tat ve sıcak bir sofra kültürü "
            "bu mutfağın temelini oluşturur."
        ),
    )
    story_quote = models.CharField(
        "Hikâye sözü", max_length=200, default="Türk mutfağının zarafeti, aynı sofrada."
    )
    menu_kicker = models.CharField("Menü üst başlığı", max_length=100, default="Günün sofrası")
    menu_title = models.CharField("Menü başlığı", max_length=100, default="Menümüz")
    menu_summary = models.CharField(
        "Menü açıklaması",
        max_length=240,
        default="Klasik tarifler, yalın sunumlar ve sofranın tanıdık lezzetleri.",
    )
    menu_note = models.CharField(
        "Menü alt notu",
        max_length=240,
        default="Ürün içerikleri ve fiyatlar işletme tarafından güncellenebilir.",
    )
    contact_kicker = models.CharField("İletişim üst başlığı", max_length=100, default="Bizi ziyaret edin")
    contact_title = models.CharField(
        "İletişim başlığı", max_length=180, default="Aynı sofrada\nbuluşalım."
    )
    contact_text = models.CharField(
        "İletişim açıklaması",
        max_length=240,
        default="Denizli Merkezefendi'deki Tomris Restoran'a ulaşmak için haritayı kullanabilirsiniz.",
    )
    address_title = models.CharField(
        "Adres ana satırı", max_length=200, default="Sırakapılar, Mimar Sinan Cd. No:30"
    )
    address_detail = models.CharField(
        "Adres ikinci satırı", max_length=200, default="20400 Merkezefendi / Denizli"
    )
    map_link = models.URLField(
        "Google Haritalar bağlantısı",
        max_length=600,
        default=(
            "https://www.google.com/maps/place/Tomris+Mini+Restoran/"
            "@37.7757214,29.0798423,17z/data=!3m1!4b1!4m6!3m5!"
            "1s0x14c73f5e8b37752b:0x70b0c9299378aaf4!8m2!"
            "3d37.7757214!4d29.0824172!16s%2Fg%2F11zbpnbmbn?"
            "entry=ttu&g_ep=EgoyMDI2MDcwOC4wIKXMDSoASAFQAw%3D%3D"
        ),
    )
    map_embed = models.URLField(
        "Harita yerleştirme bağlantısı",
        max_length=600,
        default="https://maps.google.com/maps?cid=8120211308554005236&z=17&output=embed",
    )
    opening_hours = models.CharField("Çalışma saatleri", max_length=120, default="Her gün 11.00 – 23.00")
    footer_text = models.CharField(
        "Alt bölüm yazısı", max_length=200, default="Türk mutfağının zarafeti, aynı sofrada."
    )

    class Meta:
        verbose_name = "Site ayarları"
        verbose_name_plural = "Site ayarları"

    def __str__(self):
        return "Tomris Restoran site ayarları"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
