from django.db import models


class Farmer(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    farm_type = models.CharField(max_length=120)
    avatar = models.CharField(max_length=4, default='FM')
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inquiries')
    buyer_name = models.CharField(max_length=120)
    buyer_email = models.EmailField()
    quantity = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
