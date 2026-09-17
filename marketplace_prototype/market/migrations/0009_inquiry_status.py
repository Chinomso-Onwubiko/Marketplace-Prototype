from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0008_inquiry_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='inquiry',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('replied', 'Replied'), ('closed', 'Closed')], default='pending', max_length=20),
        ),
    ]
