from datetime import date, timedelta

from django.db import migrations


def add_grapes_and_fix_categories(apps, schema_editor):
    Farmer = apps.get_model('market', 'Farmer')
    Product = apps.get_model('market', 'Product')

    Product.objects.filter(name='Kaduna Ginger').update(category='Spices')
    Product.objects.filter(name='Kano Tomatoes').update(category='Fruit')

    farmer, _ = Farmer.objects.get_or_create(
        name='Grapes from Above',
        defaults={
            'location': 'Kano, NG',
            'farm_type': 'Organic collective',
            'avatar': 'GA',
        },
    )
    Product.objects.get_or_create(
        trace_code='TRC-GRP-1256',
        defaults={
            'farmer': farmer,
            'name': "Nature's Grapes",
            'variety': 'Kudan Grapes · Organic',
            'category': 'Fruit',
            'quantity': 400,
            'unit': 'kg',
            'price': 1900,
            'harvest_date': date.today() - timedelta(days=7),
            'availability': 'Ready to waybill',
            'image_url': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?auto=format&fit=crop&w=900&q=85',
            'organic': True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0002_localize_nigerian_demo_data'),
    ]

    operations = [
        migrations.RunPython(add_grapes_and_fix_categories, migrations.RunPython.noop),
    ]