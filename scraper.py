# -*- coding: utf-8 -*-
"""
OmarVIP - Yupoo Scraper
Usage:
  python scraper.py        # scrape all
  python scraper.py 10     # scrape 10 items only
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omarvip.settings')
sys.path.insert(0, str(Path(__file__).parent))
import django
django.setup()

from store.models import Category, Product, ProductImage
from django.core.files.base import ContentFile
from django.utils.text import slugify

# Site 1 — ourvip2013 (no password)
SITE1 = {
    'base': 'https://ourvip2013.x.yupoo.com',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://ourvip2013.x.yupoo.com',
    },
    'cookies': {},
}

# Site 2 — zlwxl5201314 (password protected)
SITE2 = {
    'base': 'https://zlwxl5201314.x.yupoo.com',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://zlwxl5201314.x.yupoo.com',
    },
    'cookies': {'indexlockcode': '6662023'},
}

# Default (for backwards compat)
BASE_URL = SITE1['base']
HEADERS = SITE1['headers']

# Clean category names — skip navigation/junk albums
SKIP_KEYWORDS = ['catalog link', 'album link', 'whatsapp', 'performance', 'shipment',
                 'reviews', 'verify', 'i need', 'specified by', '简体中文', 'children']

# Known good albums — site field: 1 or 2
ALBUMS = [
    # --- Site 1 (ourvip2013) ---
    # Perfume
    {'name': 'LV Perfume',   'id': '222595023', 'site': 1},
    {'name': 'Perfume',      'id': '225982903', 'site': 1},
    # Bags
    {'name': 'Wallet',       'id': '225982023', 'site': 1},
    {'name': 'Backpack',     'id': '225980517', 'site': 1},
    {'name': 'Travel Bag',   'id': '225981465', 'site': 1},
    {'name': 'Briefcase',    'id': '225980948', 'site': 1},
    {'name': 'Suitcase',     'id': '218154145', 'site': 1},
    # Jewelry
    {'name': 'LV Jewelry',   'id': '226739061', 'site': 1},
    {'name': 'Cartier',      'id': '219725493', 'site': 1},
    # LV
    {'name': 'LV',           'id': '218914407', 'site': 1},
    {'name': 'LV Man',       'id': '226737343', 'site': 1},
    {'name': 'LV Belt Men',  'id': '226742043', 'site': 1},
    {'name': 'LV Belt Women','id': '226740295', 'site': 1},
    # Others
    {'name': 'Watch',        'id': '226508513', 'site': 1},
    {'name': 'Suit',         'id': '226490981', 'site': 1},
    {'name': 'Scarf',        'id': '217108904', 'site': 1},
    {'name': 'Hat',          'id': '217108786', 'site': 1},
    {'name': 'Belt',         'id': '217108738', 'site': 1},

    # --- Site 2 (zlwxl5201314) — Bags, Jewelry, Watches, Belts ---
    # Bags — LV
    {'name': 'LV Bags',      'category': '604993', 'site': 2},
    {'name': 'LV Wallets',   'category': '892538',  'site': 2},
    # Bags — Gucci
    {'name': 'Gucci Bags',   'category': '788753',  'site': 2},
    # Bags — Chanel
    {'name': 'Chanel Bags',  'category': '2798366', 'site': 2},
    # Bags — Dior
    {'name': 'Dior Bags',    'category': '860049',  'site': 2},
    # Bags — Hermes
    {'name': 'Hermes Bags',  'category': '588187',  'site': 2},
    # Bags — YSL
    {'name': 'YSL Bags',     'category': '577987',  'site': 2},
    # Jewelry
    {'name': 'LV Bracelets', 'category': '3276095', 'site': 2},
    # Watches
    {'name': 'Rolex',        'category': '4333306', 'site': 2},
    # Belts
    {'name': 'Leather Belt', 'category': '690679',  'site': 2},
]

import re

def clean_album_title(title, cat_name, index):
    """Extract a clean product name from a Yupoo album title."""
    if not title:
        return f'{cat_name} - Item {index}'
    # Extract model numbers like M28324, GG123, etc.
    models = re.findall(r'[A-Z]{1,3}\d{4,}', title)
    if models:
        return ' / '.join(models)
    # Strip Chinese characters and clean up
    cleaned = re.sub(r'[\u4e00-\u9fff：\-/]+', ' ', title).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    # Remove pure numbers at the start (prices)
    cleaned = re.sub(r'^\d+\s*', '', cleaned).strip()
    if cleaned:
        return cleaned
    return f'{cat_name} - Item {index}'


def make_session(site):
    s = requests.Session()
    s.headers.update(site['headers'])
    if site.get('cookies'):
        s.cookies.update(site['cookies'])
    return s


sessions = {1: make_session(SITE1), 2: make_session(SITE2)}


def get_soup(url, site_num=1):
    time.sleep(1.5)
    resp = sessions[site_num].get(url, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')


def download_image(url, site_num=1):
    try:
        time.sleep(0.3)
        resp = sessions[site_num].get(url, timeout=15)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f'    Image download failed: {e}')
        return None


def get_yupoo_user(site_num):
    """Extract the username from the site base URL."""
    base = SITE1['base'] if site_num == 1 else SITE2['base']
    return base.split('//')[1].split('.')[0]


def scrape_album_page(album_id, site_num, seen_srcs, unique_images):
    """Scrape all pages of a single album, return count of new images found."""
    site = SITE1 if site_num == 1 else SITE2
    base = site['base']
    page = 1
    total_new = 0

    while True:
        page_url = f'{base}/albums/{album_id}?uid=1&page={page}'
        try:
            soup = get_soup(page_url, site_num)
        except Exception as e:
            print(f'  Failed page {page} of album {album_id}: {e}')
            break

        main = soup.find('main') or soup
        images = main.find_all('img', src=lambda s: s and 'photo.yupoo.com' in s)
        lazy = main.find_all('img', attrs={'data-src': lambda s: s and 'photo.yupoo.com' in s})
        for img in lazy:
            img['src'] = img['data-src']
            images.append(img)

        new_found = 0
        for img in images:
            src = img.get('src', '')
            parts = src.split('/')
            base_hash = parts[-2] if len(parts) >= 2 else src
            if base_hash not in seen_srcs:
                seen_srcs.add(base_hash)
                unique_images.append((img, site_num))
                new_found += 1

        print(f'  Album {album_id} page {page}: {new_found} new images')
        total_new += new_found

        next_page = soup.find('a', string=str(page + 1))
        if not next_page:
            break
        page += 1

    return total_new


def get_sub_albums(category_id, site_num, max_albums=600):
    """Fetch sub-album IDs and titles from a category page on site 2."""
    site = SITE1 if site_num == 1 else SITE2
    base = site['base']
    albums = []  # list of (id, title)
    seen = set()
    page = 1

    while len(albums) < max_albums:
        url = f'{base}/categories/{category_id}?uid=1&page={page}'
        try:
            time.sleep(0.5)
            resp = sessions[site_num].get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            print(f'  Failed category page {page}: {e}')
            break

        links = soup.find_all('a', href=lambda h: h and '/albums/' in h)
        found = []
        for link in links:
            href = link['href']
            parts = href.split('/albums/')
            if len(parts) >= 2:
                aid = parts[1].split('?')[0].split('/')[0]
                if aid and aid.isdigit() and aid not in seen:
                    seen.add(aid)
                    # Try to get the album title from link text or title attribute
                    title = (link.get('title') or link.get_text(separator=' ', strip=True) or '').strip()
                    # Clean up title — remove extra whitespace and non-text noise
                    title = ' '.join(title.split())
                    albums.append((aid, title))
                    found.append(aid)

        print(f'  Category page {page}: {len(found)} sub-albums (total: {len(albums)})')
        if not found:
            break

        next_page = soup.find('a', string=str(page + 1))
        if not next_page:
            break
        page += 1

    return albums


def scrape_sub_album_as_product(album_id, product_name, category, site_num):
    """Scrape all images from a sub-album and save as ONE product with multiple images."""
    if Product.objects.filter(yupoo_photo_id=f'album_{album_id}').exists():
        print(f'  Skipping existing: {product_name}')
        return 0

    site = SITE1 if site_num == 1 else SITE2
    base = site['base']
    images = []
    seen_srcs = set()
    page = 1

    while True:
        page_url = f'{base}/albums/{album_id}?uid=1&page={page}'
        try:
            soup = get_soup(page_url, site_num)
        except Exception as e:
            print(f'  Failed page {page}: {e}')
            break

        main = soup.find('main') or soup
        imgs = main.find_all('img', src=lambda s: s and 'photo.yupoo.com' in s)
        lazy = main.find_all('img', attrs={'data-src': lambda s: s and 'photo.yupoo.com' in s})
        for img in lazy:
            img['src'] = img['data-src']
            imgs.append(img)

        for img in imgs:
            src = img.get('src', '')
            parts = src.split('/')
            base_hash = parts[-2] if len(parts) >= 2 else src
            if base_hash not in seen_srcs:
                seen_srcs.add(base_hash)
                images.append((img, site_num))

        next_page = soup.find('a', string=str(page + 1))
        if not next_page:
            break
        page += 1

    if not images:
        return 0

    # Reverse order so exterior shots come first, limit to 5 images
    images = list(reversed(images))[:5]

    product = Product.objects.create(
        category=category,
        name=product_name,
        yupoo_photo_id=f'album_{album_id}',
    )

    yupoo_user = None
    for order, (img_tag, sn) in enumerate(images):
        src = img_tag.get('src', '')
        parts = src.split('/')
        photo_hash = parts[-2] if len(parts) >= 2 else f'img_{order}'
        if len(parts) >= 4:
            yupoo_user = parts[3]
        img_url = f'https://photo.yupoo.com/{yupoo_user}/{photo_hash}/medium.jpg' if yupoo_user else src
        img_data = download_image(img_url, sn)
        if img_data:
            product_img = ProductImage(product=product, order=order)
            product_img.image.save(f'{photo_hash}.jpg', ContentFile(img_data), save=True)

    print(f'  Saved: {product_name} ({len(images)} images)')
    return 1


def save_images(unique_images, category, cat_name, max_items, start_index=0):
    """Download and save images to DB. Returns count saved."""
    saved = 0
    yupoo_user = None

    for i, (img_tag, site_num) in enumerate(unique_images[:max_items]):
        src = img_tag.get('src', '')
        if not src:
            continue

        parts = src.split('/')
        photo_hash = parts[-2] if len(parts) >= 2 else f'item_{i}'
        # Extract yupoo username from the image URL (3rd part: photo.yupoo.com/{user}/{hash}/...)
        if len(parts) >= 4:
            yupoo_user = parts[3]

        # Always download medium size
        img_url = f'https://photo.yupoo.com/{yupoo_user}/{photo_hash}/medium.jpg' if yupoo_user else src

        if Product.objects.filter(yupoo_photo_id=photo_hash).exists():
            print(f'  Skipping existing: {photo_hash}')
            continue

        product_name = f'{cat_name} - Item {start_index + i + 1}'
        print(f'  [{start_index + i + 1}] Downloading {product_name}...')

        img_data = download_image(img_url, site_num)
        if not img_data:
            continue

        product = Product.objects.create(
            category=category,
            name=product_name,
            yupoo_photo_id=photo_hash,
        )
        product_img = ProductImage(product=product, order=0)
        product_img.image.save(f'{photo_hash}.jpg', ContentFile(img_data), save=True)
        print(f'  Saved: {product_name}')
        saved += 1

    return saved


def scrape_album(album, max_items=500):
    name = album['name']
    site_num = album.get('site', 1)

    print(f'\n--- {name} (site {site_num}) ---')

    slug = slugify(name)
    album_id = album.get('id', album.get('category', ''))
    category, created = Category.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'yupoo_album_id': album_id}
    )
    if created:
        print(f'  Created category: {name}')

    seen_srcs = set()
    unique_images = []

    if 'category' in album:
        # Site 2: category → multiple sub-albums, each sub-album = 1 product
        print(f'  Fetching sub-albums for category {album["category"]}...')
        sub_albums = get_sub_albums(album['category'], site_num)
        print(f'  Found {len(sub_albums)} sub-albums')
        saved = 0
        for i, (aid, title) in enumerate(sub_albums[:max_items]):
            product_name = clean_album_title(title, name, i + 1)
            saved += scrape_sub_album_as_product(aid, product_name, category, site_num)
        print(f'  Done — saved {saved} products')
        return saved
    else:
        # Site 1: direct album — each image is a separate product
        scrape_album_page(album['id'], site_num, seen_srcs, unique_images)
        print(f'  Total unique images: {len(unique_images)}')
        saved = save_images(unique_images, category, name, max_items)
        print(f'  Done — saved {saved} items')
        return saved


PERFUME_ALBUMS = [a for a in ALBUMS if 'perfume' in a['name'].lower()]


def main(limit=None, category_filter=None):
    print('=== OmarVIP Yupoo Scraper ===\n')

    albums = ALBUMS
    if category_filter:
        albums = [a for a in ALBUMS if category_filter.lower() in a['name'].lower()]
        print(f'Filtering for: {category_filter} → {len(albums)} albums\n')

    total = 0
    for album in albums:
        if limit and total >= limit:
            break
        remaining = (limit - total) if limit else 500
        total += scrape_album(album, max_items=remaining)

    print(f'\n=== Done! Total saved: {total} products ===')
    print(f'Total in database: {Product.objects.count()}')


if __name__ == '__main__':
    # Usage:
    #   python scraper.py              → all albums
    #   python scraper.py 50           → 50 items total
    #   python scraper.py all perfume  → all perfumes
    #   python scraper.py 50 perfume   → 50 perfumes
    args = sys.argv[1:]
    limit = None
    category_filter = None

    for arg in args:
        if arg.isdigit():
            limit = int(arg)
        elif arg != 'all':
            category_filter = arg

    main(limit=limit, category_filter=category_filter)
