from django.db import migrations


# İlk kurulumda (0002/0004) eklenen örnek/demo ürünler.
DEMO_PRODUCTS = (
    "Mercimek Çorbası",
    "Ezogelin Çorbası",
    "Fırın Makarna",
    "Kremalı Tavuklu Makarna",
    "Pilav Üstü Kavurma",
    "Etli Kuru Fasulye",
    "Fırın Sütlaç",
    "Cevizli Baklava",
    "Türk Çayı",
    "Ev Limonatası",
)

# Demo kategoriler: yalnızca içinde ürün kalmazsa silinir
# (kullanıcının admin'den eklediği ürünler varsa kategori korunur).
DEMO_CATEGORY_SLUGS = ("soups", "mains", "desserts", "drinks")

# Geri alma için demo verinin özgün hâli.
RESTORE_CATEGORIES = (
    ("soups", "Çorbalar", "Günlük sıcak", 10),
    ("mains", "Ana Yemekler", "Mutfağın seçkisi", 20),
    ("desserts", "Tatlılar", "Sofranın sonu", 30),
    ("drinks", "İçecekler", "Sofraya eşlik edenler", 40),
)
RESTORE_PRODUCTS = (
    ("Mercimek Çorbası", "soups", "Tereyağı ve pul biber eşliğinde", "140.00", 10),
    ("Ezogelin Çorbası", "soups", "Nane ve limon eşliğinde", "150.00", 20),
    ("Fırın Makarna", "mains", "Kaşar rendesiyle fırınlanmış", "260.00", 10),
    ("Kremalı Tavuklu Makarna", "mains", "Mantar ve taze krema soslu", "320.00", 20),
    ("Pilav Üstü Kavurma", "mains", "Tereyağlı pilav ve dana kavurma", "420.00", 30),
    ("Etli Kuru Fasulye", "mains", "Tereyağlı pilav ve turşu eşliğinde", "340.00", 40),
    ("Fırın Sütlaç", "desserts", "Fırında karamelize, fındık kırığıyla", "180.00", 10),
    ("Cevizli Baklava", "desserts", "Kaymak eşliğinde", "220.00", 20),
    ("Türk Çayı", "drinks", "İnce belli bardakta", "40.00", 10),
    ("Ev Limonatası", "drinks", "Taze sıkım, naneli", "90.00", 20),
)


def remove_demo(apps, schema_editor):
    MenuCategory = apps.get_model("restaurant", "MenuCategory")
    Product = apps.get_model("restaurant", "Product")

    Product.objects.filter(name__in=DEMO_PRODUCTS).delete()

    for slug in DEMO_CATEGORY_SLUGS:
        category = MenuCategory.objects.filter(slug=slug).first()
        if category and not category.products.exists():
            category.delete()


def restore_demo(apps, schema_editor):
    MenuCategory = apps.get_model("restaurant", "MenuCategory")
    Product = apps.get_model("restaurant", "Product")

    categories = {}
    for slug, name, eyebrow, sort_order in RESTORE_CATEGORIES:
        category, _ = MenuCategory.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "eyebrow": eyebrow,
                "sort_order": sort_order,
                "is_active": True,
            },
        )
        categories[slug] = category

    for name, category_slug, description, price, sort_order in RESTORE_PRODUCTS:
        Product.objects.update_or_create(
            name=name,
            defaults={
                "category": categories[category_slug],
                "description": description,
                "price": price,
                "sort_order": sort_order,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0009_seed_new_menu_items")]

    operations = [migrations.RunPython(remove_demo, restore_demo)]
