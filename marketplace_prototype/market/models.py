from django.contrib.auth.models import User
from django.db import models


class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='farmer')
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    farm_type = models.CharField(max_length=120)
    avatar = models.CharField(max_length=4, default='FM')
    email = models.EmailField(blank=True, null=True)
    verified = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=120)
    variety = models.CharField(max_length=120)
    category = models.CharField(max_length=60)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, default='kg')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    harvest_date = models.DateField()
    availability = models.CharField(max_length=40, default='Available now')
    image_url = models.URLField()
    trace_code = models.CharField(max_length=40, unique=True)
    organic = models.BooleanField(default=False)

    class Meta:
        ordering = ['-harvest_date']

    def __str__(self):
        return self.name


class Inquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inquiries')
    buyer_name = models.CharField(max_length=120)
    buyer_email = models.EmailField()
    quantity = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_message = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
