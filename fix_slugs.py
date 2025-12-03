"""
Quick script to fix vendor slugs
Run this from the event_vendor directory with: uv run python fix_slugs.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'event'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event.settings')
django.setup()

from django.utils.text import slugify
from vendors.models import Vendor

# Find vendors with empty slugs
vendors_without_slug = Vendor.objects.filter(slug='') | Vendor.objects.filter(slug__isnull=True)
count = vendors_without_slug.count()

if count == 0:
    print('✓ No vendors with empty slugs found.')
    sys.exit(0)

print(f'Found {count} vendor(s) with empty slugs. Fixing...\n')

for vendor in vendors_without_slug:
    base_slug = slugify(vendor.name)
    slug = base_slug
    counter = 1

    while Vendor.objects.filter(slug=slug).exclude(pk=vendor.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    vendor.slug = slug
    vendor.save(update_fields=['slug'])
    print(f'✓ Fixed slug for "{vendor.name}": {slug}')

print(f'\n✓ Successfully fixed {count} vendor slug(s).')
