from django.db import migrations
from django.db.models import Max


CATEGORIES = (
    ("bowl", "Bowl", "Doyurucu kaseler"),
    ("makarna", "Makarna", "Penne çeşitleri"),
    ("salata", "Salata", "Taze ve hafif"),
    ("fastfood", "Fastfood", "Tost çeşitleri"),
    ("pilav", "Pilav", "Pilav üstü lezzetler"),
)

PRODUCTS = (
    ("Izgara Tavuklu Bowl", "bowl", "Izgara tavuk, taze yeşillik, pilav", 10),
    ("Çıtır Tavuklu Bowl", "bowl", "Çıtır tavuk, sebze ve özel sos", 20),
    ("Körili Tavuklu Bowl", "bowl", "Köri soslu tavuk, pirinç", 30),
    ("Sweet Chili Bowl", "bowl", "Sweet chili soslu tavuk", 40),
    ("Ateşli Bowl", "bowl", "Acı soslu, ateşli lezzet", 50),
    ("Ton Balıklı Makarnalı Bowl", "bowl", "Ton balığı, penne, sebze", 60),
    ("Protein Bowl", "bowl", "Yüksek protein, dengeli tabak", 70),
    ("Günaydın Bowl", "bowl", "Yumurta, avokado, güne başlangıç", 80),
    ("Ege Bowl", "bowl", "Zeytinyağlı, Ege usulü taze", 90),
    ("Türk İşi Bowl", "bowl", "Yerel lezzetler, Türk usulü", 100),
    ("Vegan Bowl", "bowl", "%100 bitkisel, doyurucu tabak", 110),
    ("Vejeteryan Bowl", "bowl", "Sebze ağırlıklı, etsiz", 120),
    ("Tavuklu Makarnalı Bowl", "bowl", "Tavuk, penne, kremsi sos", 130),
    ("Kremalı Mantarlı Tavuklu Penne", "makarna", "Kremalı mantar sosu, tavuk", 10),
    ("Körili Tavuklu Penne", "makarna", "Köri soslu tavuklu penne", 20),
    ("Acı Soslu Tavuklu Penne", "makarna", "Acı sos, tavuk, penne", 30),
    ("Ton Balıklı Mısırlı Penne", "makarna", "Ton balığı, mısır, penne", 40),
    ("Sweet Chili Penne", "makarna", "Sweet chili soslu penne", 50),
    ("Domates Soslu Penne", "makarna", "Ev usulü domates sosu", 60),
    ("Salçalı Yoğurtlu Penne", "makarna", "Salçalı sos, sarımsaklı yoğurt", 70),
    ("Pesto Soslu Penne", "makarna", "Fesleğenli pesto sosu", 80),
    ("Izgara Tavuklu Salata", "salata", "Izgara tavuk, karışık yeşillik", 10),
    ("Çıtır Tavuklu Salata", "salata", "Çıtır tavuk, taze sebze", 20),
    ("Ton Balıklı Salata", "salata", "Ton balığı, mevsim yeşillikleri", 30),
    ("Yeşil Mercimekli Salata", "salata", "Yeşil mercimek, taze otlar", 40),
    ("Çıtır Nohutlu Salata", "salata", "Fırın nohut, bol yeşillik", 50),
    ("Üç Peynirli Salata", "salata", "Üç çeşit peynir, roka", 60),
    ("Akdeniz Salata", "salata", "Zeytin, peynir, Akdeniz usulü", 70),
    ("Çoban Salata", "salata", "Domates, salatalık, soğan", 80),
    ("Sucuklu Tost", "fastfood", "Bol sucuklu klasik tost", 10),
    ("Kaşarlı Tost", "fastfood", "Eriyen kaşarlı tost", 20),
    ("Yumurtalı Tost", "fastfood", "Yumurtalı sıcak tost", 30),
    ("Sucuklu Kaşarlı Tost", "fastfood", "Sucuk ve kaşar birlikte", 40),
    ("Sucuklu Yumurtalı Tost", "fastfood", "Sucuk ve yumurta", 50),
    ("Yumurtalı Kaşarlı Tost", "fastfood", "Yumurta ve kaşar", 60),
    ("Full Karışık Tost", "fastfood", "Sucuk, kaşar, yumurta — hepsi bir arada", 70),
    ("Tomris Atom Tost", "fastfood", "Acı ve bol malzemeli özel tost", 80),
    ("Ton Balıklı Mısırlı Tost", "fastfood", "Ton balığı ve mısır", 90),
    ("Pesto Soslu Avokadolu Tost", "fastfood", "Pesto, avokado, taze", 100),
    ("Cheddarlı Kaşarlı Mısırlı Tost", "fastfood", "Cheddar, kaşar, mısır", 110),
    ("Izgara Tavuklu Pilav", "pilav", "Izgara tavuk üzeri tereyağlı pilav", 10),
    ("Kremalı Tavuklu Pilav", "pilav", "Kremalı tavuk, pilav", 20),
    ("Körili Tavuklu Pilav", "pilav", "Köri soslu tavuk, pilav", 30),
    ("Ton Balıklı Mısırlı Pilav", "pilav", "Ton balığı, mısır, pilav", 40),
    ("Çıtır Tavuklu Pilav", "pilav", "Çıtır tavuk, pilav", 50),
    ("Köfteli Pilav", "pilav", "Izgara köfte, tereyağlı pilav", 60),
    ("Acı Soslu Tavuklu Pilav", "pilav", "Acı soslu tavuk, pilav", 70),
    ("Sweetchili Tavuklu Pilav", "pilav", "Sweet chili tavuk, pilav", 80),
    ("Arabiata Tavuklu Pilav", "pilav", "Arabiata sos, tavuk, pilav", 90),
)


def seed_menu(apps, schema_editor):
    MenuCategory = apps.get_model("restaurant", "MenuCategory")
    Product = apps.get_model("restaurant", "Product")

    # Yeni kategoriler, mevcut kategorilerin (sırası ne olursa olsun) sonuna eklenir.
    new_slugs = [item[0] for item in CATEGORIES]
    existing_max = (
        MenuCategory.objects.exclude(slug__in=new_slugs)
        .aggregate(Max("sort_order"))["sort_order__max"]
        or 0
    )

    categories = {}
    for index, (slug, name, eyebrow) in enumerate(CATEGORIES, start=1):
        category, _ = MenuCategory.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "eyebrow": eyebrow,
                "sort_order": existing_max + index * 10,
                "is_active": True,
            },
        )
        categories[slug] = category

    for name, category_slug, description, sort_order in PRODUCTS:
        Product.objects.update_or_create(
            name=name,
            category=categories[category_slug],
            defaults={
                "description": description,
                "price": "0.00",
                "sort_order": sort_order,
                "is_active": True,
            },
        )


def remove_menu(apps, schema_editor):
    MenuCategory = apps.get_model("restaurant", "MenuCategory")
    Product = apps.get_model("restaurant", "Product")

    slugs = [item[0] for item in CATEGORIES]
    Product.objects.filter(category__slug__in=slugs).delete()
    MenuCategory.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0008_product_responsive_images")]

    operations = [migrations.RunPython(seed_menu, remove_menu)]
