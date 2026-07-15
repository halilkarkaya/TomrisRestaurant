from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("restaurant", "0006_site_contact_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="hero_lead",
            field=models.CharField(
                blank=True,
                default="Türk mutfağının tanıdık lezzetleri, aynı sofrada özenle buluşuyor.",
                max_length=240,
                verbose_name="Ana sayfa açıklaması",
            ),
        ),
    ]
