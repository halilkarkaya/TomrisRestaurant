from decimal import Decimal
from io import BytesIO
from tempfile import mkdtemp

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import MenuCategory, Product, SiteSettings


class HomePageTests(TestCase):
    def setUp(self):
        Product.objects.all().delete()
        self.soup_category = MenuCategory.objects.get(slug="soups")
        self.visible_product = Product.objects.create(
            name="Test Çorbası",
            category=self.soup_category,
            description="Günlük hazırlanır",
            ingredients="Mercimek, soğan ve havuç",
            allergen_info="Gluten içerebilir.",
            price=Decimal("125.00"),
            sort_order=1,
            is_active=True,
        )
        Product.objects.create(
            name="Gizli Ürün",
            category=self.soup_category,
            price=Decimal("99.00"),
            sort_order=2,
            is_active=False,
        )

    def test_home_page_renders_active_database_products(self):
        response = self.client.get(reverse("restaurant:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Çorbası")
        self.assertNotContains(response, "Gizli Ürün")

    def test_home_page_contains_requested_denizli_address_and_map(self):
        response = self.client.get(reverse("restaurant:home"))

        self.assertContains(response, "Mimar Sinan Cd. No:30")
        self.assertContains(response, "Merkezefendi / Denizli")
        self.assertContains(response, "google.com/maps")
        self.assertIn("Tomris+Mini+Restoran", response.context["site"].map_link)
        self.assertIn("cid=8120211308554005236", response.context["site"].map_embed)

    def test_home_page_has_all_menu_category_anchors(self):
        response = self.client.get(reverse("restaurant:home"))

        for anchor in ("soups", "mains", "desserts", "drinks"):
            self.assertContains(response, f'id="{anchor}"')

    def test_site_settings_are_rendered_on_home_page(self):
        settings = SiteSettings.load()
        settings.menu_title = "Bugünün Lezzetleri"
        settings.opening_hours = "Salı – Pazar 12.00 – 22.00"
        settings.save()

        response = self.client.get(reverse("restaurant:home"))

        self.assertContains(response, "Bugünün Lezzetleri")
        self.assertContains(response, "Salı – Pazar 12.00 – 22.00")

    def test_hero_highlights_the_turkish_flag_responsively(self):
        response = self.client.get(reverse("restaurant:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "hero__tribute")
        self.assertContains(response, "turk-bayragi-kumas.webp")
        self.assertContains(response, "hero__flag-fallback")
        self.assertContains(response, "data-flag-image")
        self.assertContains(response, "Cumhuriyetin ışığında")

    def test_menu_product_links_to_its_detail_page(self):
        response = self.client.get(reverse("restaurant:home"))

        self.assertContains(response, self.visible_product.get_absolute_url())
        self.assertIn("test-corbasi", self.visible_product.get_absolute_url())

    def test_active_product_detail_page_shows_product_information(self):
        response = self.client.get(self.visible_product.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Çorbası")
        self.assertContains(response, "Mercimek, soğan ve havuç")
        self.assertContains(response, "Gluten içerebilir.")

    def test_hidden_product_detail_page_returns_not_found(self):
        hidden_product = Product.objects.get(name="Gizli Ürün")

        response = self.client.get(hidden_product.get_absolute_url())

        self.assertEqual(response.status_code, 404)


class ContactInfoTests(TestCase):
    def test_phone_href_normalizes_turkish_numbers(self):
        site_settings = SiteSettings.load()

        site_settings.phone_number = "0258 263 00 00"
        self.assertEqual(site_settings.phone_href, "tel:+902582630000")

        site_settings.phone_number = "+90 (532) 111 22 33"
        self.assertEqual(site_settings.phone_href, "tel:+905321112233")

        site_settings.phone_number = ""
        self.assertEqual(site_settings.phone_href, "")

    def test_contact_links_render_when_filled(self):
        site_settings = SiteSettings.load()
        site_settings.phone_number = "0258 263 00 00"
        site_settings.whatsapp_number = "0532 111 22 33"
        site_settings.instagram_url = "https://www.instagram.com/tomrisrestoran"
        site_settings.facebook_url = "https://www.facebook.com/tomrisrestoran"
        site_settings.save()

        response = self.client.get(reverse("restaurant:home"))

        self.assertContains(response, 'href="tel:+902582630000"')
        self.assertContains(response, "0258 263 00 00")
        self.assertContains(response, "https://wa.me/905321112233")
        self.assertContains(response, "whatsapp-float")
        self.assertContains(response, "https://www.instagram.com/tomrisrestoran")
        self.assertContains(response, "https://www.facebook.com/tomrisrestoran")

    def test_contact_links_hidden_when_blank(self):
        response = self.client.get(reverse("restaurant:home"))

        self.assertNotContains(response, "tel:+")
        self.assertNotContains(response, "wa.me")
        self.assertNotContains(response, "whatsapp-float")
        self.assertNotContains(response, "site-footer__social")


class ErrorPageTests(TestCase):
    def test_custom_404_template_is_used(self):
        response = self.client.get("/boyle-bir-sayfa-yok/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "Aradığınız sayfa bulunamadı", status_code=404)

    def test_custom_500_template_renders_without_database(self):
        from django.template.loader import render_to_string

        html = render_to_string("500.html")

        self.assertIn("Beklenmeyen bir sorun oluştu", html)
        self.assertIn("Ana sayfaya dön", html)


@override_settings(MEDIA_ROOT=mkdtemp(prefix="tomris-test-media-"))
class ImageShrinkTests(TestCase):
    def _jpeg_upload(self, width, height):
        buffer = BytesIO()
        Image.new("RGB", (width, height), "#8f2428").save(buffer, format="JPEG")
        return SimpleUploadedFile("test-foto.jpg", buffer.getvalue(), content_type="image/jpeg")

    def _create_product(self, upload):
        return Product.objects.create(
            name="Foto Testi",
            category=MenuCategory.objects.get(slug="soups"),
            price=Decimal("100.00"),
            image=upload,
        )

    def test_large_product_image_is_shrunk_on_save(self):
        product = self._create_product(self._jpeg_upload(2400, 1600))

        with Image.open(product.image.path) as saved:
            self.assertEqual((saved.width, saved.height), (1200, 800))

    def test_small_product_image_is_kept_as_is(self):
        product = self._create_product(self._jpeg_upload(800, 500))

        with Image.open(product.image.path) as saved:
            self.assertEqual((saved.width, saved.height), (800, 500))

    def test_large_hero_image_is_shrunk_on_save(self):
        site_settings = SiteSettings.load()
        buffer = BytesIO()
        Image.new("RGB", (3200, 1800), "#2a170c").save(buffer, format="JPEG")
        site_settings.hero_image = SimpleUploadedFile(
            "hero-foto.jpg", buffer.getvalue(), content_type="image/jpeg"
        )
        site_settings.save()

        with Image.open(site_settings.hero_image.path) as saved:
            self.assertEqual((saved.width, saved.height), (1920, 1080))

    def test_resaving_existing_product_does_not_create_duplicate_file(self):
        product = self._create_product(self._jpeg_upload(2400, 1600))
        stored_name = product.image.name

        product.refresh_from_db()
        product.price = Decimal("150.00")
        product.save()

        self.assertEqual(product.image.name, stored_name)


@override_settings(MEDIA_ROOT=mkdtemp(prefix="tomris-test-media-"))
class ProductAdminTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin-test",
            email="admin@example.com",
            password="not-a-real-password-123",
        )
        self.client.force_login(self.user)

    def test_product_admin_is_available_to_superuser(self):
        response = self.client.get(reverse("admin:restaurant_product_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ürünler")
        self.assertContains(response, "Menü durumu")

    def test_admin_home_explains_all_management_tasks(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Menünüzü buradan yönetin")
        self.assertContains(response, "Kategorileri düzenle")
        self.assertContains(response, "Site yazılarını düzenle")

    def test_product_form_contains_image_and_plain_language_help(self):
        response = self.client.get(reverse("admin:restaurant_product_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ürün resmi")
        self.assertContains(response, "Müşterilerin menüde göreceği ürün adını yazın.")
        self.assertContains(response, "Kategorideki yeri")
        self.assertContains(response, "1 yazarsanız kategoride en üstte görünür")

    def test_admin_shows_plain_positions_instead_of_internal_sort_values(self):
        product = Product.objects.order_by("category__sort_order", "sort_order").first()
        product.sort_order = 30
        product.save(update_fields=("sort_order",))

        response = self.client.get(reverse("admin:restaurant_product_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kategorideki yeri")
        self.assertContains(response, "1. sıra (en üstte)")

    def test_saving_a_plain_position_reorders_products(self):
        products = list(Product.objects.filter(category__slug="soups").order_by("sort_order"))
        moved_product = products[-1]

        response = self.client.post(
            reverse("admin:restaurant_product_change", args=(moved_product.pk,)),
            {
                "name": moved_product.name,
                "category": moved_product.category_id,
                "description": moved_product.description,
                "ingredients": moved_product.ingredients,
                "allergen_info": moved_product.allergen_info,
                "price": moved_product.price,
                "is_active": "on",
                "position": 1,
                "_save": "Kaydet",
            },
        )

        self.assertEqual(response.status_code, 302)
        first_product = Product.objects.filter(category=moved_product.category).order_by("sort_order").first()
        self.assertEqual(first_product.pk, moved_product.pk)

    def test_category_and_site_settings_admin_are_available(self):
        category_response = self.client.get(
            reverse("admin:restaurant_menucategory_changelist")
        )
        site_response = self.client.get(
            reverse("admin:restaurant_sitesettings_changelist")
        )

        self.assertEqual(category_response.status_code, 200)
        self.assertContains(category_response, "Menü kategorileri")
        self.assertEqual(site_response.status_code, 200)
        self.assertContains(site_response, "Marka ve ana sayfa görseli")
