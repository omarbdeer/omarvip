from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True)
    name_he = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    yupoo_album_id = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    yupoo_photo_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
