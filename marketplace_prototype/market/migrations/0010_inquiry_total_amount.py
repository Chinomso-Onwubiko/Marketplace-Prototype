from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0009_inquiry_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='inquiry',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
