from django.db import migrations, models


MAP_LINK = (
    "https://www.google.com/maps/place/Tomris+Mini+Restoran/"
    "@37.7757214,29.0798423,17z/data=!3m1!4b1!4m6!3m5!"
    "1s0x14c73f5e8b37752b:0x70b0c9299378aaf4!8m2!"
    "3d37.7757214!4d29.0824172!16s%2Fg%2F11zbpnbmbn?"
    "entry=ttu&g_ep=EgoyMDI2MDcwOC4wIKXMDSoASAFQAw%3D%3D"
)
MAP_EMBED = "https://maps.google.com/maps?cid=8120211308554005236&z=17&output=embed"

OLD_MAP_LINK = (
    "https://www.google.com/maps/place//data=!4m2!3m1!"
    "1s0x14c73f5e8b37752b:0x70b0c9299378aaf4?sa=X&ved=1t:8290&ictx=111"
)
OLD_MAP_EMBED = (
    "https://www.google.com/maps?q=S%C4%B1rakap%C4%B1lar%2C%20Mimar%20Sinan%20Cd.%20"
    "No%3A30%2C%2020400%20Merkezefendi%2FDenizli&output=embed"
)


def update_map(apps, schema_editor):
    SiteSettings = apps.get_model("restaurant", "SiteSettings")
    SiteSettings.objects.update(map_link=MAP_LINK, map_embed=MAP_EMBED)


def restore_map(apps, schema_editor):
    SiteSettings = apps.get_model("restaurant", "SiteSettings")
    SiteSettings.objects.update(map_link=OLD_MAP_LINK, map_embed=OLD_MAP_EMBED)


class Migration(migrations.Migration):
    dependencies = [("restaurant", "0004_manage_categories_site_and_images")]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="map_link",
            field=models.URLField(default=MAP_LINK, max_length=600, verbose_name="Google Haritalar bağlantısı"),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="map_embed",
            field=models.URLField(default=MAP_EMBED, max_length=600, verbose_name="Harita yerleştirme bağlantısı"),
        ),
        migrations.RunPython(update_map, restore_map),
    ]
