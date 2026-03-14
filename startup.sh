#!/bin/sh
set -e

python manage.py migrate --noinput

# Load base data (categories + original products)
python manage.py loaddata store/fixtures/initial_data.json

# Clear the 10 new categories and reload with correct products
python manage.py shell -c "
from store.models import Category, Product
cats = ['LV Bags','LV Wallets','Gucci Bags','Chanel Bags','Dior Bags','Hermes Bags','YSL Bags','LV Bracelets','Rolex','Leather Belt']
for name in cats:
    try:
        cat = Category.objects.get(name=name)
        deleted = cat.products.all().delete()
        print(f'Cleared {name}')
    except Category.DoesNotExist:
        pass
"

# Load clean new products
python manage.py loaddata store/fixtures/new_cats.json

echo "Startup complete"
exec gunicorn omarvip.wsgi:application --bind 0.0.0.0:$PORT
