from django.db import migrations


# Ürün adı -> görsel dosya kökü (media/products/<slug>.webp ve varyantları).
NAME_TO_SLUG = {
    "Izgara Tavuklu Bowl": "izgara-tavuklu-bowl",
    "Çıtır Tavuklu Bowl": "citir-tavuklu-bowl",
    "Körili Tavuklu Bowl": "korili-tavuklu-bowl",
    "Sweet Chili Bowl": "sweet-chili-bowl",
    "Ateşli Bowl": "atesli-bowl",
    "Ton Balıklı Makarnalı Bowl": "ton-balikli-makarnali-bowl",
    "Protein Bowl": "protein-bowl",
    "Günaydın Bowl": "gunaydin-bowl",
    "Ege Bowl": "ege-bowl",
    "Türk İşi Bowl": "turk-isi-bowl",
    "Vegan Bowl": "vegan-bowl",
    "Vejeteryan Bowl": "vejeteryan-bowl",
    "Tavuklu Makarnalı Bowl": "tavuklu-makarnali-bowl",
    "Kremalı Mantarlı Tavuklu Penne": "kremali-mantarli-tavuklu-penne",
    "Körili Tavuklu Penne": "korili-tavuklu-penne",
    "Acı Soslu Tavuklu Penne": "aci-soslu-tavuklu-penne",
    "Ton Balıklı Mısırlı Penne": "ton-balikli-misirli-penne",
    "Sweet Chili Penne": "sweet-chili-penne",
    "Domates Soslu Penne": "domates-soslu-penne",
    "Salçalı Yoğurtlu Penne": "salcali-yogurtlu-penne",
    "Pesto Soslu Penne": "pesto-soslu-penne",
    "Izgara Tavuklu Salata": "izgara-tavuklu-salata",
    "Çıtır Tavuklu Salata": "citir-tavuklu-salata",
    "Ton Balıklı Salata": "ton-balikli-salata",
    "Yeşil Mercimekli Salata": "yesil-mercimekli-salata",
    "Çıtır Nohutlu Salata": "citir-nohutlu-salata",
    "Üç Peynirli Salata": "uc-peynirli-salata",
    "Akdeniz Salata": "akdeniz-salata",
    "Çoban Salata": "coban-salata",
    "Sucuklu Tost": "sucuklu-tost",
    "Kaşarlı Tost": "kasarli-tost",
    "Yumurtalı Tost": "yumurtali-tost",
    "Sucuklu Kaşarlı Tost": "sucuklu-kasarli-tost",
    "Sucuklu Yumurtalı Tost": "sucuklu-yumurtali-tost",
    "Yumurtalı Kaşarlı Tost": "yumurtali-kasarli-tost",
    "Full Karışık Tost": "full-karisik-tost",
    "Tomris Atom Tost": "tomris-atom-tost",
    "Ton Balıklı Mısırlı Tost": "ton-balikli-misirli-tost",
    "Pesto Soslu Avokadolu Tost": "pesto-soslu-avokadolu-tost",
    "Cheddarlı Kaşarlı Mısırlı Tost": "cheddarli-kasarli-misirli-tost",
    "Izgara Tavuklu Pilav": "izgara-tavuklu-pilav",
    "Kremalı Tavuklu Pilav": "kremali-tavuklu-pilav",
    "Körili Tavuklu Pilav": "korili-tavuklu-pilav",
    "Ton Balıklı Mısırlı Pilav": "ton-balikli-misirli-pilav",
    "Çıtır Tavuklu Pilav": "citir-tavuklu-pilav",
    "Köfteli Pilav": "kofteli-pilav",
    "Acı Soslu Tavuklu Pilav": "aci-soslu-tavuklu-pilav",
    "Sweetchili Tavuklu Pilav": "sweetchili-tavuklu-pilav",
    "Arabiata Tavuklu Pilav": "arabiata-tavuklu-pilav",
}


def set_images(apps, schema_editor):
    Product = apps.get_model("restaurant", "Product")
    for name, slug in NAME_TO_SLUG.items():
        Product.objects.filter(name=name).update(
            image=f"products/{slug}.webp",
            image_480=f"products/{slug}-480.webp",
            image_960=f"products/{slug}-960.webp",
        )


def clear_images(apps, schema_editor):
    Product = apps.get_model("restaurant", "Product")
    Product.objects.filter(name__in=NAME_TO_SLUG).update(
        image="", image_480="", image_960=""
    )


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0010_remove_demo_products")]

    operations = [migrations.RunPython(set_images, clear_images)]
