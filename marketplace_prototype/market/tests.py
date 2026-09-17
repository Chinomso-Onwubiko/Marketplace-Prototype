import json

from django.core import mail
from django.test import TestCase

from market.models import Farmer, Inquiry, Product
from market.views import seed_demo_data


class ProductImageUrlTests(TestCase):
    def test_affected_products_use_direct_image_urls(self):
        seed_demo_data()

        problematic_products = {
            'Benue Cassava',
            'Kano Onions',
            'Abia Plantain',
            'Ogun Cocoa Beans',
            'Kaduna Groundnuts',
            'Benue Soybeans',
            'Kano Cowpeas',
        }

        for product_name in problematic_products:
            product = Product.objects.get(name=product_name)
            self.assertTrue(product.image_url.startswith('https://'))
            self.assertNotIn('commons.wikimedia.org/wiki/Special:FilePath', product.image_url)

    def test_inquiry_form_has_csrf_token(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_farmer_can_login_and_view_own_dashboard(self):
        seed_demo_data()
        farmer = Farmer.objects.filter(user__isnull=False).first()
        self.assertIsNotNone(farmer)

        response = self.client.post('/farmer/login/', {'username': farmer.user.username, 'password': 'farmer123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/farmer/dashboard/')

        dashboard = self.client.get('/farmer/dashboard/')
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, farmer.name)

    def test_farmer_can_send_follow_up_email_to_buyer(self):
        seed_demo_data()
        farmer = Farmer.objects.filter(user__isnull=False).first()
        product = Product.objects.filter(farmer=farmer).first()
        inquiry = Inquiry.objects.create(
            product=product,
            buyer_name='Test Buyer',
            buyer_email='buyer@example.com',
            quantity=25,
            note='Interested in supply',
        )

        self.client.force_login(farmer.user)
        response = self.client.post(
            f'/farmer/inquiries/{inquiry.pk}/respond/',
            {'message': 'We can deliver next week.'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(any('We can deliver next week.' in email.body for email in mail.outbox))
        self.assertEqual(mail.outbox[-1].to, ['buyer@example.com'])
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, 'replied')

    def test_farmer_can_update_inquiry_status(self):
        seed_demo_data()
        farmer = Farmer.objects.filter(user__isnull=False).first()
        product = Product.objects.filter(farmer=farmer).first()
        inquiry = Inquiry.objects.create(
            product=product,
            buyer_name='Status Buyer',
            buyer_email='status@example.com',
            quantity=10,
            note='Need update',
        )

        self.client.force_login(farmer.user)
        response = self.client.post(
            f'/farmer/inquiries/{inquiry.pk}/status/',
            {'status': 'closed'},
        )

        self.assertEqual(response.status_code, 302)
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, 'closed')

    def test_cart_submission_creates_inquiry_visible_in_farmer_dashboard(self):
        seed_demo_data()
        product = Product.objects.first()
        farmer = product.farmer

        self.client.post(f'/cart/add/{product.pk}/', {'quantity': 2})
        response = self.client.post(
            '/inquire/',
            {
                'buyer_name': 'Jane Buyer',
                'buyer_email': 'jane@example.com',
                'note': 'Need delivery this week',
                'cart': json.dumps([{'product_id': product.pk, 'quantity': 2}]),
            },
        )

        self.assertEqual(response.status_code, 302)
        inquiry = Inquiry.objects.filter(product=product, buyer_email='jane@example.com').first()
        self.assertIsNotNone(inquiry)
        self.assertEqual(inquiry.quantity, 2)

        self.client.force_login(farmer.user)
        dashboard = self.client.get('/farmer/dashboard/')
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, 'Jane Buyer')
