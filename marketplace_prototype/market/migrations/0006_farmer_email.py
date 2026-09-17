from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_update_ginger_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmer',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
