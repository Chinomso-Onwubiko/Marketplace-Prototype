from django.test import TestCase

from market.models import Farmer, Product
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
