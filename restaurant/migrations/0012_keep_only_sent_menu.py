from django.db import migrations


# Kullanıcının gönderdiği menü (menu.html) yalnızca bu 5 kategoriden oluşur.
# Bunların dışındaki tüm ürün ve kategoriler kaldırılır.
KEEP_CATEGORY_SLUGS = ("bowl", "makarna", "salata", "fastfood", "pilav")


def keep_only_sent_menu(apps, schema_editor):
    MenuCategory = apps.get_model("restaurant", "MenuCategory")
    Product = apps.get_model("restaurant", "Product")

    Product.objects.exclude(category__slug__in=KEEP_CATEGORY_SLUGS).delete()
    MenuCategory.objects.exclude(slug__in=KEEP_CATEGORY_SLUGS).delete()


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0011_menu_item_photos")]

    # Silinen özel veri (ör. kullanıcının eklediği ürün/kategori) geri
    # yüklenemez; bu adım ileri yönlü tek yönlü bir temizliktir.
    operations = [migrations.RunPython(keep_only_sent_menu, migrations.RunPython.noop)]
