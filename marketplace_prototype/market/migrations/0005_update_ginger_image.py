from django.db import migrations


def update_ginger_image(apps, schema_editor):
    Product = apps.get_model('market', 'Product')
    Product.objects.filter(trace_code='TRC-GIN-2406').update(
        image_url='https://images.unsplash.com/photo-1630623093145-f606591c2546?auto=format&fit=crop&w=900&q=85',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0004_update_ginger_tomato_images'),
    ]

    operations = [
        migrations.RunPython(update_ginger_image, migrations.RunPython.noop),
    ]