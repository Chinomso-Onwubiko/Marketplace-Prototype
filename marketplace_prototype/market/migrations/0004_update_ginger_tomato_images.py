from django.db import migrations


def update_product_images(apps, schema_editor):
    Product = apps.get_model('market', 'Product')
    Product.objects.filter(trace_code='TRC-GIN-2406').update(
        image_url='https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=900&q=85',
    )
    Product.objects.filter(trace_code='TRC-TOM-3190').update(
        image_url='https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=900&q=85',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0003_add_grapes_and_fix_categories'),
    ]

    operations = [
        migrations.RunPython(update_product_images, migrations.RunPython.noop),
    ]