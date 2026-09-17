from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .models import Farmer, Inquiry, Product


def seed_demo_data():
    farmer_data = [
        ('Amina Bello Farms', 'Kaduna, NG', 'Family farm', 'AB', 'amina@aminabellofarms.ng'),
        ('Benue Valley Growers', 'Benue, NG', 'Co-op', 'BV', 'hello@benuevalleygrowers.ng'),
        ('Kano Green Collective', 'Kano, NG', 'Organic collective', 'KG', 'sales@kanogreencollective.ng'),
        ('Grapes from Above', 'Kano, NG', 'Organic collective', 'GA', 'orders@grapesfromabove.ng'),
        ('Ube 001', 'Abia, NG', 'Family farm', 'UB', 'chisomdivine81@gmail.com'),
        ('Ijebu Garri', 'Ogun, NG', 'Family farm', 'GR', 'inquiries@ijebugarri.ng'),
        ('Farm Plateau', 'Plateau, NG', 'Co-op', 'FP', 'hello@farmplateau.ng'),
    ]
    farmers = {}
    for name, location, farm_type, avatar, email in farmer_data:
        farmer, _ = Farmer.objects.get_or_create(
            name=name,
            defaults={'location': location, 'farm_type': farm_type, 'avatar': avatar, 'email': email},
        )
        if not farmer.email:
            farmer.email = email
            farmer.save(update_fields=['email'])

        username = name.lower().replace(' ', '_')
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'first_name': name.split()[0]},
        )
        if user_created:
            user.set_password('farmer123')
            user.save(update_fields=['password'])
        if not farmer.user_id or farmer.user_id != user.pk:
            farmer.user = user
            farmer.save(update_fields=['user'])
        farmers[name] = farmer

    product_data = [
        (farmers['Amina Bello Farms'], 'Kaduna Ginger', 'Yellow ginger · Grade A', 'Spices', 820, 3500, 2, 'Ready to waybill', 'https://images.unsplash.com/photo-1630623093145-f606591c2546?auto=format&fit=crop&w=900&q=85', 'TRC-GIN-2406', True),
        (farmers['Benue Valley Growers'], 'Benue Rice', 'Local long grain · 2025 crop', 'Grains', 2400, 2200, 38, 'Available now', 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=900&q=85', 'TRC-RIC-8812', False),
        (farmers['Kano Green Collective'], 'Kano Tomatoes', 'Roma tomato · Fresh harvest', 'Fruit', 360, 1800, 1, 'Dispatch in 3 days', 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=900&q=85', 'TRC-TOM-3190', True),
        (farmers['Grapes from Above'], "Nature's Grapes", 'Kudan Grapes · Organic', 'Fruit', 400, 1900, 7, 'Ready to waybill', 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?auto=format&fit=crop&w=900&q=85', 'TRC-GRP-1256', True),
        (farmers['Ube 001'], 'Fresh Ube', 'Eastern pear · Organic', 'Fruit', 500, 3900, 5, 'Ready to waybill', 'https://foodsguy.com/wp-content/uploads/2023/06/ube-african-pear-1024x707.jpg', 'TRC-GRP-7866', True),
        (farmers['Ijebu Garri'], 'Garri Ijebu', 'Ijebu Garri · Organic', 'Grains', 300, 1000, 2, 'Ready to waybill', 'https://th.bing.com/th/id/OIP.BnSguO1OWqfAernHLzYjNwHaFz?w=227&h=180&c=7&r=0&o=7&dpr=1.5&pid=1.7&rm=3', 'TRC-GRP-5366', True),
        (farmers['Amina Bello Farms'], 'Kaduna Maize', 'White maize · Grade A', 'Grains', 1800, 1450, 12, 'Available now', 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=900&q=85', 'TRC-MAI-4101', False),
        (farmers['Benue Valley Growers'], 'Benue Cassava', 'Fresh cassava roots · Bulk lot', 'Grains', 2200, 950, 4, 'Ready to waybill', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUwi4Livtd_izZN05kiU8HNQ2DqgU2OHU5g5pMgSXEsfde0gdn2keVyCas&s=10', 'TRC-CAS-4102', True),
        (farmers['Kano Green Collective'], 'Kano Onions', 'Red onions · Market grade', 'Spices', 1200, 2800, 3, 'Available now', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoBR-MaNbKEu6QW94coTGW9Ad_0Re5CFGDYvoxeYyhlQ&s=10', 'TRC-ONI-4103', False),
        (farmers['Ube 001'], 'Abia Plantain', 'Green plantain · Cooking grade', 'Fruit', 900, 2400, 2, 'Ready to waybill', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTV6AcGNhpMKwZV5C0_L7OgiiscUEtOjW1JmJBo1lzpFA&s=10', 'TRC-PLA-4104', True),
        (farmers['Ijebu Garri'], 'Garri Bendel', 'Yellow Garri · Cooking grade', 'Grains', 900, 1300, 2, 'Ready to waybill', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6OAqhjQW7lCwUoQmnpq2Qp2bpuj_BTogD7cCv-ck7yg&s=10', 'TRC-GAR-4113', True),
        (farmers['Ijebu Garri'], 'Ogun Cocoa Beans', 'Fermented cocoa · Export grade', 'Grains', 650, 6200, 18, 'Dispatch in 5 days', 'https://www.whitakerschocolates.com/cdn/shop/articles/Facts-About-Cocoa-Beans_520x500_a5d7ca72-2582-4327-83ce-22f0278028f9.jpg?v=1772645596', 'TRC-COC-4105', False),
        (farmers['Amina Bello Farms'], 'Kaduna Groundnuts', 'Shelled groundnuts · Premium', 'Grains', 740, 3100, 9, 'Available now', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTrogwgJWXdpbnrZ3XEafBU7Gx__2OwMY9u82XKPVZFlw&s', 'TRC-GRO-4106', False),
        (farmers['Benue Valley Growers'], 'Benue Soybeans', 'Yellow soybean · Cleaned', 'Grains', 1100, 2700, 21, 'Available now', 'https://i.ebayimg.com/images/g/5ZAAAOSwvZ5f61~Q/s-l1200.jpg', 'TRC-SOY-4107', False),
        (farmers['Kano Green Collective'], 'Kano Cowpeas', 'Brown beans · Sorted', 'Grains', 580, 3600, 15, 'Ready to waybill', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRuTFXkB2h0HQzn2C2PiHz9rgMljoKyEeqh-sFGu_kNGd20wEYwOVWv-k&s=10', 'TRC-COW-4108', False),
        (farmers['Ube 001'], 'Abia Yam', 'White yam · Market tubers', 'Grains', 1500, 2300, 6, 'Available now', 'https://images.unsplash.com/photo-1757283961544-e161ac41b201?auto=format&fit=crop&w=900&q=85', 'TRC-YAM-4109', True),
        (farmers['Ijebu Garri'], 'Ogun Scotch Bonnet', 'Fresh pepper · Hot variety', 'Spices', 260, 4200, 1, 'Ready to ship', 'https://images.unsplash.com/photo-1743670476802-886108356b1d?auto=format&fit=crop&w=900&q=85', 'TRC-PEP-4110', True),
        (farmers['Benue Valley Growers'], 'Benue Watermelon', 'Red flesh · Fresh harvest', 'Fruit', 780, 1700, 2, 'Dispatch in 2 days', 'https://images.unsplash.com/photo-1563114773-84221bd62daa?auto=format&fit=crop&w=900&q=85', 'TRC-WAT-4111', False),
        (farmers['Kano Green Collective'], 'Kano Sesame', 'White sesame · Cleaned seed', 'Spices', 430, 4800, 25, 'Available now', 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=900&q=85', 'TRC-SES-4112', False),
    ]
    for farmer, name, variety, category, quantity, price, days_old, availability, image_url, trace_code, organic in product_data:
        product, _ = Product.objects.get_or_create(
            trace_code=trace_code,
            defaults={
                'farmer': farmer,
                'name': name,
                'variety': variety,
                'category': category,
                'quantity': quantity,
                'unit': 'kg',
                'price': price,
                'harvest_date': date.today() - timedelta(days=days_old),
                'availability': availability,
                'image_url': image_url,
                'organic': organic,
            },
        )
        if product.image_url != image_url:
            product.image_url = image_url
            product.save(update_fields=['image_url'])


def dashboard(request):
    seed_demo_data()
    products = Product.objects.select_related('farmer').all()
    category = request.GET.get('category', 'All products')
    search = request.GET.get('q', '').strip()
    if category != 'All products':
        products = products.filter(category=category)
    if search:
        products = products.filter(name__icontains=search)
    context = {
        'products': products,
        'category': category,
        'search': search,
        'categories': ['All products', 'Fruit', 'Grains', 'Spices'],
        'farmer_count': Farmer.objects.count(),
        'supply_count': Product.objects.count(),
        'inquiry_count': Inquiry.objects.count(),
    }
    return render(request, 'market/dashboard.html', context)


def inquire(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        inquiry = Inquiry.objects.create(
            product=product,
            buyer_name=request.POST.get('buyer_name', '').strip(),
            buyer_email=request.POST.get('buyer_email', '').strip(),
            quantity=int(request.POST.get('quantity', 0) or 0),
            note=request.POST.get('note', '').strip(),
        )

        if product.farmer.email:
            send_mail(
                subject=f'New inquiry for {product.name}',
                message=(
                    f'Buyer name: {inquiry.buyer_name}\n'
                    f'Buyer email: {inquiry.buyer_email}\n'
                    f'Product: {product.name}\n'
                    f'Batch code: {product.trace_code}\n'
                    f'Quantity requested: {inquiry.quantity} {product.unit}\n'
                    f'Note: {inquiry.note or "No additional note"}\n'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[product.farmer.email],
                fail_silently=False,
            )

        messages.success(request, f'Inquiry sent to {product.farmer.name}. They will respond within one business day.')
    return redirect('dashboard')


def farmer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'farmer'):
            login(request, user)
            return redirect('farmer_dashboard')
        messages.error(request, 'Invalid farmer credentials.')
    return render(request, 'market/farmer_login.html')


@login_required(login_url='farmer_login')
def farmer_dashboard(request):
    if not hasattr(request.user, 'farmer'):
        logout(request)
        return redirect('farmer_login')

    inquiries = Inquiry.objects.filter(product__farmer=request.user.farmer).select_related('product', 'product__farmer').order_by('-created_at')
    context = {
        'farmer': request.user.farmer,
        'inquiries': inquiries,
    }
    return render(request, 'market/farmer_dashboard.html', context)


@login_required(login_url='farmer_login')
def farmer_logout(request):
    logout(request)
    return redirect('farmer_login') 