from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("restaurant", "0007_alter_sitesettings_hero_lead"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image_480",
            field=models.ImageField(
                blank=True,
                editable=False,
                upload_to="products/variants/",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="image_960",
            field=models.ImageField(
                blank=True,
                editable=False,
                upload_to="products/variants/",
            ),
        ),
    ]
