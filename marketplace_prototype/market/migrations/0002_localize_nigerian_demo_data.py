from django.db import migrations


def localize_demo_data(apps, schema_editor):
    Farmer = apps.get_model('market', 'Farmer')
    Product = apps.get_model('market', 'Product')

    farmers = [
        ('Maya & Sons Farm', 'Amina Bello Farms', 'Kaduna, NG', 'AB'),
        ('Riverside Growers', 'Benue Valley Growers', 'Benue, NG', 'BV'),
        ('Green Valley Collective', 'Kano Green Collective', 'Kano, NG', 'KG'),
    ]
    for old_name, new_name, location, avatar in farmers:
        Farmer.objects.filter(name=old_name).update(name=new_name, location=location, avatar=avatar)

    products = [
        ('Alphonso Mangoes', 'Kaduna Ginger', 'Yellow ginger · Grade A', 3500, 'TRC-GIN-2406'),
        ('Basmati Rice', 'Benue Rice', 'Local long grain · 2025 crop', 2200, 'TRC-RIC-8812'),
        ('Turmeric Fingers', 'Kano Tomatoes', 'Roma tomato · Fresh harvest', 1800, 'TRC-TOM-3190'),
    ]
    for old_name, new_name, variety, price, trace_code in products:
        Product.objects.filter(name=old_name).update(
            name=new_name,
            variety=variety,
            price=price,
            trace_code=trace_code,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(localize_demo_data, migrations.RunPython.noop),
    ]