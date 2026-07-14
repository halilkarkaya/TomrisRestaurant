from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.utils.html import format_html

from .models import MenuCategory, Product, SiteSettings


admin.site.site_header = "Tomris Restoran"
admin.site.site_title = "Tomris Yönetim"
admin.site.index_title = "Site ve Menü Yönetimi"
admin.site.unregister(Group)
admin.site.unregister(User)


def position_label(position):
    return f"{position}. sıra" + (" (en üstte)" if position == 1 else "")


def ordered_position(queryset, obj):
    ordered_ids = list(queryset.values_list("pk", flat=True))
    try:
        return ordered_ids.index(obj.pk) + 1
    except ValueError:
        return len(ordered_ids) + 1


class MenuCategoryAdminForm(forms.ModelForm):
    position = forms.IntegerField(
        label="Menüdeki yeri",
        min_value=1,
        help_text="1 yazarsanız en üstte görünür; 2 ikinci sırada, 3 üçüncü sırada görünür.",
        widget=forms.NumberInput(attrs={"min": 1, "step": 1}),
    )

    class Meta:
        model = MenuCategory
        fields = "__all__"
        exclude = ("sort_order",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = MenuCategory.objects.order_by("sort_order", "name", "pk")
        if self.instance.pk:
            self.fields["position"].initial = ordered_position(categories, self.instance)
        else:
            self.fields["position"].initial = categories.count() + 1


class ProductAdminForm(forms.ModelForm):
    position = forms.IntegerField(
        label="Kategorideki yeri",
        min_value=1,
        help_text="1 yazarsanız kategoride en üstte görünür; 2 ikinci sırada, 3 üçüncü sırada görünür.",
        widget=forms.NumberInput(attrs={"min": 1, "step": 1}),
    )

    class Meta:
        model = Product
        fields = "__all__"
        exclude = ("sort_order",)
        labels = {
            "is_active": "Menüde göster",
        }
        help_texts = {
            "name": "Müşterilerin menüde göreceği ürün adını yazın.",
            "category": "Ürünün sitede hangi başlık altında görüneceğini seçin.",
            "image": "Kare veya yatay bir yemek fotoğrafı yükleyin. JPG, PNG veya WebP olabilir.",
            "description": "Sunum veya önemli bir özelliği kısa bir cümleyle anlatın.",
            "ingredients": "Üründe kullanılan temel malzemeleri virgülle ayırarak yazın.",
            "allergen_info": "Gluten, süt ürünü, yumurta veya kuruyemiş gibi önemli bilgileri yazın.",
            "price": "Türk lirası olarak yazın. Örnek: 250,00",
            "is_active": "İşaretliyse ürün internet sitesindeki menüde görünür.",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Örnek: Mercimek Çorbası"}),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Örnek: Tereyağı ve çıtır ekmek ile servis edilir.",
                }
            ),
            "ingredients": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Örnek: Mercimek, soğan, havuç, tereyağı, baharatlar",
                }
            ),
            "allergen_info": forms.TextInput(
                attrs={"placeholder": "Örnek: Gluten ve süt ürünü içerir."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.category_id:
            products = Product.objects.filter(category_id=self.instance.category_id).order_by(
                "sort_order", "name", "pk"
            )
            self.fields["position"].initial = ordered_position(products, self.instance)
        else:
            self.fields["position"].initial = 1


class ProductInline(admin.TabularInline):
    model = Product
    fields = ("name", "price", "is_active")
    extra = 0
    show_change_link = True
    verbose_name = "Bu kategorideki ürün"
    verbose_name_plural = "Bu kategorideki ürünler"


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    form = MenuCategoryAdminForm
    list_display = ("name", "eyebrow", "product_count", "is_active", "menu_position")
    list_editable = ("is_active",)
    list_display_links = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "eyebrow")
    ordering = ("sort_order", "name")
    inlines = (ProductInline,)
    fieldsets = (
        (
            "Kategorinin menüde görünen bilgileri",
            {
                "description": "Örnek: Çorbalar / Günlük sıcak",
                "fields": ("name", "eyebrow", "slug"),
            },
        ),
        (
            "Gösterim ayarları",
            {"fields": ("is_active", "position")},
        ),
    )

    @admin.display(description="Ürün sayısı")
    def product_count(self, obj):
        return obj.products.count()

    @admin.display(description="Menüdeki yeri", ordering="sort_order")
    def menu_position(self, obj):
        before = MenuCategory.objects.filter(
            Q(sort_order__lt=obj.sort_order)
            | Q(sort_order=obj.sort_order, name__lt=obj.name)
            | Q(sort_order=obj.sort_order, name=obj.name, pk__lt=obj.pk)
        ).count()
        return position_label(before + 1)

    def save_model(self, request, obj, form, change):
        requested_position = form.cleaned_data["position"]
        obj.sort_order = 1_000_000
        super().save_model(request, obj, form, change)

        categories = list(MenuCategory.objects.exclude(pk=obj.pk).order_by("sort_order", "name", "pk"))
        insert_at = min(requested_position - 1, len(categories))
        categories.insert(insert_at, obj)
        for index, category in enumerate(categories, start=1):
            category.sort_order = index * 10
        MenuCategory.objects.bulk_update(categories, ("sort_order",))


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        "image_thumbnail",
        "name",
        "category",
        "formatted_price",
        "menu_status",
        "category_position",
        "updated_at",
    )
    list_display_links = ("image_thumbnail", "name")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description", "ingredients")
    search_help_text = "Ürün adı, açıklaması veya içindekilerde ara."
    ordering = ("category__sort_order", "sort_order", "name")
    list_per_page = 30
    save_on_top = True
    readonly_fields = ("image_preview", "created_at", "updated_at")
    actions = ("publish_products", "hide_products")
    empty_value_display = "—"
    fieldsets = (
        (
            "Menüde görünen bilgiler",
            {
                "description": "Müşterilerin internet sitesinde göreceği bilgileri doldurun.",
                "fields": (
                    "name",
                    "category",
                    "image",
                    "image_preview",
                    "description",
                    "ingredients",
                    "allergen_info",
                    "price",
                ),
            },
        ),
        (
            "Gösterim ayarları",
            {
                "description": "Ürünü yayına alın veya kategorideki yerini belirleyin.",
                "fields": ("is_active", "position"),
            },
        ),
        (
            "Kayıt bilgileri",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    @admin.display(description="Resim")
    def image_thumbnail(self, obj):
        if not obj.image:
            return "—"
        return format_html(
            '<img class="admin-product-thumb" src="{}" alt="">', obj.image.url
        )

    @admin.display(description="Mevcut resim")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "Henüz ürün resmi eklenmedi."
        return format_html(
            '<img class="admin-product-preview" src="{}" alt="{} resmi">',
            obj.image.url,
            obj.name,
        )

    @admin.display(description="Fiyat", ordering="price")
    def formatted_price(self, obj):
        return f"{obj.price:,.2f} ₺".replace(",", "X").replace(".", ",").replace("X", ".")

    @admin.display(description="Menü durumu", ordering="is_active")
    def menu_status(self, obj):
        modifier = "visible" if obj.is_active else "hidden"
        label = "Menüde" if obj.is_active else "Gizli"
        return format_html(
            '<span class="menu-status menu-status--{}">{}</span>',
            modifier,
            label,
        )

    @admin.display(description="Kategorideki yeri", ordering="sort_order")
    def category_position(self, obj):
        before = Product.objects.filter(category=obj.category).filter(
            Q(sort_order__lt=obj.sort_order)
            | Q(sort_order=obj.sort_order, name__lt=obj.name)
            | Q(sort_order=obj.sort_order, name=obj.name, pk__lt=obj.pk)
        ).count()
        return position_label(before + 1)

    def save_model(self, request, obj, form, change):
        old_category_id = None
        if obj.pk:
            old_category_id = Product.objects.filter(pk=obj.pk).values_list(
                "category_id", flat=True
            ).first()

        requested_position = form.cleaned_data["position"]
        obj.sort_order = 1_000_000
        super().save_model(request, obj, form, change)

        products = list(
            Product.objects.filter(category=obj.category)
            .exclude(pk=obj.pk)
            .order_by("sort_order", "name", "pk")
        )
        insert_at = min(requested_position - 1, len(products))
        products.insert(insert_at, obj)
        for index, product in enumerate(products, start=1):
            product.sort_order = index * 10
        Product.objects.bulk_update(products, ("sort_order",))

        if old_category_id and old_category_id != obj.category_id:
            old_products = list(
                Product.objects.filter(category_id=old_category_id).order_by(
                    "sort_order", "name", "pk"
                )
            )
            for index, product in enumerate(old_products, start=1):
                product.sort_order = index * 10
            Product.objects.bulk_update(old_products, ("sort_order",))

    @admin.action(description="Seçilen ürünleri menüde göster")
    def publish_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{updated} ürün internet sitesindeki menüde gösteriliyor.",
            messages.SUCCESS,
        )

    @admin.action(description="Seçilen ürünleri menüden gizle")
    def hide_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} ürün internet sitesindeki menüden gizlendi.",
            messages.SUCCESS,
        )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ("hero_image_preview",)
    fieldsets = (
        (
            "Marka ve ana sayfa görseli",
            {
                "fields": (
                    ("brand_name", "brand_type"),
                    "hero_image",
                    "hero_image_preview",
                    "hero_eyebrow",
                    ("hero_title_first", "hero_title_second"),
                    "hero_lead",
                )
            },
        ),
        (
            "Hakkımızda bölümü",
            {"fields": ("story_kicker", "story_title", "story_intro", "story_body", "story_quote")},
        ),
        (
            "Menü bölümü",
            {"fields": ("menu_kicker", "menu_title", "menu_summary", "menu_note")},
        ),
        (
            "İletişim, adres ve harita",
            {
                "fields": (
                    "contact_kicker",
                    "contact_title",
                    "contact_text",
                    "address_title",
                    "address_detail",
                    "opening_hours",
                    "map_link",
                    "map_embed",
                )
            },
        ),
        ("Alt bölüm", {"fields": ("footer_text",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        settings_obj = SiteSettings.load()
        return self.change_view(request, str(settings_obj.pk), extra_context=extra_context)

    @admin.display(description="Mevcut ana görsel")
    def hero_image_preview(self, obj):
        if not obj or not obj.hero_image:
            return "Özel görsel eklenmedi; varsayılan Atatürk görseli kullanılıyor."
        return format_html(
            '<img class="admin-hero-preview" src="{}" alt="Ana sayfa görseli">',
            obj.hero_image.url,
        )
