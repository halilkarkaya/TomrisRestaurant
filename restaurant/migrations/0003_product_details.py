from django.db import migrations, models


DETAILS = {
    ("soups", 10): (
        "Kırmızı mercimek, soğan, havuç, un, tereyağı ve baharatlar",
        "Gluten ve süt ürünü içerir.",
    ),
    ("soups", 20): (
        "Kırmızı mercimek, bulgur, pirinç, soğan, domates, nane ve baharatlar",
        "Gluten içerebilir.",
    ),
    ("mains", 10): (
        "Makarna, süt, tereyağı, un, yumurta ve kaşar peyniri",
        "Gluten, süt ürünü ve yumurta içerir.",
    ),
    ("mains", 20): (
        "Makarna, tavuk eti, mantar, krema, sarımsak ve baharatlar",
        "Gluten ve süt ürünü içerir.",
    ),
    ("mains", 30): (
        "Dana eti, pirinç, tereyağı, et suyu ve baharatlar",
        "Süt ürünü içerir.",
    ),
    ("mains", 40): (
        "Kuru fasulye, dana eti, domates, soğan, tereyağı ve baharatlar",
        "Süt ürünü içerir.",
    ),
    ("desserts", 10): (
        "Süt, pirinç, şeker, nişasta, yumurta ve fındık",
        "Süt ürünü, yumurta ve fındık içerir.",
    ),
    ("desserts", 20): (
        "Baklavalık yufka, ceviz, tereyağı, şeker ve limon",
        "Gluten, süt ürünü ve ceviz içerir.",
    ),
    ("drinks", 10): (
        "Siyah çay ve su",
        "Belirtilmiş alerjen içermez.",
    ),
    ("drinks", 20): (
        "Limon, su, şeker ve taze nane",
        "Belirtilmiş alerjen içermez.",
    ),
}


def add_product_details(apps, schema_editor):
    Product = apps.get_model("restaurant", "Product")
    for (category, sort_order), (ingredients, allergen_info) in DETAILS.items():
        Product.objects.filter(category=category, sort_order=sort_order).update(
            ingredients=ingredients,
            allergen_info=allergen_info,
        )


def remove_product_details(apps, schema_editor):
    Product = apps.get_model("restaurant", "Product")
    Product.objects.update(ingredients="", allergen_info="")


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0002_seed_products")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="ingredients",
            field=models.TextField(blank=True, verbose_name="İçindekiler"),
        ),
        migrations.AddField(
            model_name="product",
            name="allergen_info",
            field=models.CharField(blank=True, max_length=200, verbose_name="Alerjen bilgisi"),
        ),
        migrations.RunPython(add_product_details, remove_product_details),
    ]
