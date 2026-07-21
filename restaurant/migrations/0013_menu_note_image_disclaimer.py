from django.db import migrations, models


OLD_NOTE = "Ürün içerikleri ve fiyatlar işletme tarafından güncellenebilir."
NEW_NOTE = (
    "Ürün görselleri temsilidir. "
    "Ürün içerikleri ve fiyatlar işletme tarafından güncellenebilir."
)


def add_image_disclaimer(apps, schema_editor):
    SiteSettings = apps.get_model("restaurant", "SiteSettings")
    # Yalnızca hâlâ varsayılan metni kullanan kaydı güncelle;
    # işletme admin'den özelleştirdiyse dokunma.
    SiteSettings.objects.filter(menu_note=OLD_NOTE).update(menu_note=NEW_NOTE)


def remove_image_disclaimer(apps, schema_editor):
    SiteSettings = apps.get_model("restaurant", "SiteSettings")
    SiteSettings.objects.filter(menu_note=NEW_NOTE).update(menu_note=OLD_NOTE)


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0012_keep_only_sent_menu")]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="menu_note",
            field=models.CharField(
                default=NEW_NOTE, max_length=240, verbose_name="Menü alt notu"
            ),
        ),
        migrations.RunPython(add_image_disclaimer, remove_image_disclaimer),
    ]
