from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Company, Perfume, PerfumeSize, Product, ProductImage


# --- Legacy admin (kept so old data is still editable; can be deleted later) ---

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ar', 'name_he', 'slug', 'image']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name']
    inlines = [ProductImageInline]


# --- The Perfume Legend ---

class PerfumeSizeInline(admin.TabularInline):
    model = PerfumeSize
    extra = 2
    fields = ['size_ml', 'price']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['logo_thumb', 'name', 'perfume_count', 'created_at']
    list_display_links = ['logo_thumb', 'name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    fields = ['name', 'slug', 'logo', 'description']

    @admin.display(description='Logo')
    def logo_thumb(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;">',
                obj.logo.url,
            )
        return '—'

    @admin.display(description='Perfumes')
    def perfume_count(self, obj):
        return obj.perfumes.count()


@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = ['image_thumb', 'name', 'company', 'gender', 'size_summary', 'created_at']
    list_display_links = ['image_thumb', 'name']
    list_filter = ['company', 'gender']
    search_fields = ['name', 'company__name']
    autocomplete_fields = ['company']
    inlines = [PerfumeSizeInline]
    fields = ['name', 'company', 'gender', 'image', 'description']

    @admin.display(description='Image')
    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;">',
                obj.image.url,
            )
        return '—'

    @admin.display(description='Sizes')
    def size_summary(self, obj):
        sizes = obj.sizes.all()
        if not sizes:
            return '—'
        return ', '.join(f'{s.size_ml}ml' for s in sizes)
