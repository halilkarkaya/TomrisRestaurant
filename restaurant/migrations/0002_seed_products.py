from django.db import migrations


PRODUCTS = (
    ("Mercimek Çorbası", "soups", "Tereyağı ve pul biber eşliğinde", "140.00", 10),
    ("Ezogelin Çorbası", "soups", "Nane ve limon eşliğinde", "150.00", 20),
    ("Fırın Makarna", "mains", "Kaşar rendesiyle fırınlanmış", "260.00", 10),
    (
        "Kremalı Tavuklu Makarna",
        "mains",
        "Mantar ve taze krema soslu",
        "320.00",
        20,
    ),
    ("Pilav Üstü Kavurma", "mains", "Tereyağlı pilav ve dana kavurma", "420.00", 30),
    (
        "Etli Kuru Fasulye",
        "mains",
        "Tereyağlı pilav ve turşu eşliğinde",
        "340.00",
        40,
    ),
    ("Fırın Sütlaç", "desserts", "Fırında karamelize, fındık kırığıyla", "180.00", 10),
    ("Cevizli Baklava", "desserts", "Kaymak eşliğinde", "220.00", 20),
    ("Türk Çayı", "drinks", "İnce belli bardakta", "40.00", 10),
    ("Ev Limonatası", "drinks", "Taze sıkım, naneli", "90.00", 20),
)


def seed_products(apps, schema_editor):
    Product = apps.get_model("restaurant", "Product")
    for name, category, description, price, sort_order in PRODUCTS:
        Product.objects.update_or_create(
            name=name,
            defaults={
                "category": category,
                "description": description,
                "price": price,
                "sort_order": sort_order,
                "is_active": True,
            },
        )


def remove_seeded_products(apps, schema_editor):
    Product = apps.get_model("restaurant", "Product")
    Product.objects.filter(name__in=[item[0] for item in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0001_initial")]

    operations = [migrations.RunPython(seed_products, remove_seeded_products)]
