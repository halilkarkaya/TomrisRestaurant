from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("restaurant", "0013_menu_note_image_disclaimer"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="show_product_images",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Kapattığınızda menü ve ürün detay sayfalarındaki yemek "
                    "fotoğrafları gizlenir."
                ),
                verbose_name="Ürün görsellerini sitede göster",
            ),
        ),
    ]
