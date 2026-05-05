from django.db import models
from django.utils.text import slugify


# --- Legacy models (kept for migration compatibility; no longer used by public site) ---

class Category(models.Model):
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True)
    name_he = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    yupoo_album_id = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories (legacy)'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    yupoo_photo_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Products (legacy)'

    def __str__(self):
        return self.name

    def first_image(self):
        return self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


# --- The Perfume Legend ---

class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='companies/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Perfume(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('U', 'Unisex'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='perfumes')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='perfumes/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['company__name', 'name']

    def __str__(self):
        return f'{self.company.name} — {self.name}'


class PerfumeSize(models.Model):
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, related_name='sizes')
    size_ml = models.PositiveIntegerField(help_text='Size in millilitres')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['size_ml']
        unique_together = [('perfume', 'size_ml')]

    def __str__(self):
        return f'{self.size_ml}ml'
