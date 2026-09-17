from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0007_farmer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='inquiry',
            name='response_message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inquiry',
            name='responded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
