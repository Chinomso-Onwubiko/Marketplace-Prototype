import json
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Farmer, Inquiry, Product


def get_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']


def cart_count(request):
    return sum(int(qty) for qty in get_cart(request).values())


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
        'cart_count': cart_count(request),
    }
    return render(request, 'market/dashboard.html', context)


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


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = get_cart(request)
    quantity = int(request.POST.get('quantity', 1) or 1)
    cart[str(product.id)] = int(cart.get(str(product.id), 0)) + max(1, quantity)
    request.session.modified = True

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        data = {'ok': True, 'cart_count': cart_count(request), 'product_name': product.name}
        return JsonResponse(data)

    messages.success(request, f'{product.name} added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


def cart_view(request):
    cart = get_cart(request)
    items = []
    total = Decimal('0.00')
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        line_total = Decimal(str(product.price)) * int(quantity)
        total += line_total
        items.append({
            'product': product,
            'quantity': int(quantity),
            'line_total': line_total,
        })
    context = {
        'items': items,
        'total': total,
        'cart_count': cart_count(request),
        'cart_json': json.dumps([
            {'product_id': int(product_id), 'quantity': int(quantity)}
            for product_id, quantity in cart.items()
        ]),
    }
    return render(request, 'market/cart.html', context)


def update_cart(request, product_id):
    cart = get_cart(request)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 0) or 0)
        if qty <= 0:
            cart.pop(str(product_id), None)
        else:
            cart[str(product_id)] = qty
        request.session.modified = True
    return redirect('cart')


def remove_from_cart(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
    return redirect('cart')


def _parse_cart_items(request, product_id=None):
    cart_data = request.POST.get('cart')
    if cart_data:
        try:
            parsed = json.loads(cart_data)
        except (TypeError, ValueError, json.JSONDecodeError):
            parsed = []

        if isinstance(parsed, dict):
            parsed = [parsed]
        if isinstance(parsed, list):
            return parsed

    return [{
        'product_id': request.POST.get('product_id') or product_id,
        'quantity': request.POST.get('quantity', 1) or 1,
    }]


def inquire(request, product_id=None):
    if request.method != 'POST':
        return redirect('dashboard')

    cart_items = _parse_cart_items(request, product_id)
    if not cart_items:
        messages.error(request, 'Please add at least one product to your cart before confirming the order.')
        return redirect('dashboard')

    buyer_name = request.POST.get('buyer_name', '').strip()
    buyer_email = request.POST.get('buyer_email', '').strip()
    note = request.POST.get('note', '').strip()

    if not buyer_name or not buyer_email:
        messages.error(request, 'Please provide your name and email before confirming the order.')
        return redirect('dashboard')

    created_inquiries = []
    order_total = Decimal('0.00')

    for item in cart_items:
        if not isinstance(item, dict):
            continue
        product_id_value = item.get('product_id')
        quantity_value = item.get('quantity', 1)
        if product_id_value is None:
            continue

        product = get_object_or_404(Product, pk=product_id_value)
        quantity = max(1, int(quantity_value or 1))
        line_total = Decimal(str(product.price)) * quantity
        order_total += line_total

        inquiry = Inquiry.objects.create(
            product=product,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            quantity=quantity,
            note=note,
            total_amount=line_total,
        )
        created_inquiries.append(inquiry)

        if product.farmer.email:
            send_mail(
                subject=f'New inquiry for {product.name}',
                message=(
                    f'Buyer name: {inquiry.buyer_name}\n'
                    f'Buyer email: {inquiry.buyer_email}\n'
                    f'Product: {product.name}\n'
                    f'Batch code: {product.trace_code}\n'
                    f'Quantity requested: {inquiry.quantity} {product.unit}\n'
                    f'Line total: ₦{line_total:.2f}\n'
                    f'Note: {inquiry.note or "No additional note"}\n'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[product.farmer.email],
                fail_silently=False,
            )

    buyer_message = (
        'Hello there, your order request has been received, we would get back to you with a follow up message '
        'within 24hours, thank you.'
    )
    send_mail(
        subject='Order request received',
        message=f'{buyer_message}\n\nOrder total: ₦{order_total:.2f}\nItems: {", ".join(f"{inq.product.name} x {inq.quantity}" for inq in created_inquiries)}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[buyer_email],
        fail_silently=False,
    )

    if created_inquiries:
        first_product = created_inquiries[0].product
        messages.success(request, f'Order confirmed for {first_product.name}. A confirmation email has been sent to {buyer_email}.')

    request.session['cart'] = {}
    request.session.modified = True
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
def respond_to_inquiry(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, pk=inquiry_id, product__farmer=request.user.farmer)

    if request.method == 'POST':
        message = (request.POST.get('message', '') or '').strip()
        if not message:
            messages.error(request, 'Please enter a follow-up message before sending.')
            return redirect('farmer_dashboard')

        send_mail(
            subject=f'Re: inquiry for {inquiry.product.name}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.buyer_email],
            fail_silently=False,
        )

        inquiry.response_message = message
        inquiry.responded_at = timezone.now()
        inquiry.status = 'replied'
        inquiry.save(update_fields=['response_message', 'responded_at', 'status'])
        messages.success(request, 'Your follow-up message has been sent to the buyer.')

    return redirect('farmer_dashboard')


@login_required(login_url='farmer_login')
def update_inquiry_status(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, pk=inquiry_id, product__farmer=request.user.farmer)

    if request.method == 'POST':
        new_status = request.POST.get('status', 'pending')
        if new_status in dict(Inquiry.STATUS_CHOICES):
            inquiry.status = new_status
            inquiry.save(update_fields=['status'])
            messages.success(request, f'Inquiry status updated to {inquiry.get_status_display()}.')
        else:
            messages.error(request, 'Invalid inquiry status selected.')

    return redirect('farmer_dashboard')


@login_required(login_url='farmer_login')
def farmer_logout(request):
    logout(request)
    return redirect('farmer_login') 