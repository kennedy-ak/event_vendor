from django.core.management.base import BaseCommand
from django.utils.text import slugify
from vendors.models import Vendor


class Command(BaseCommand):
    help = 'Fix vendors with missing or empty slugs'

    def handle(self, *args, **options):
        vendors_without_slug = Vendor.objects.filter(slug='') | Vendor.objects.filter(slug__isnull=True)
        count = vendors_without_slug.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No vendors with empty slugs found.'))
            return

        self.stdout.write(f'Found {count} vendor(s) with empty slugs. Fixing...')

        for vendor in vendors_without_slug:
            base_slug = slugify(vendor.name)
            slug = base_slug
            counter = 1

            while Vendor.objects.filter(slug=slug).exclude(pk=vendor.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            vendor.slug = slug
            vendor.save(update_fields=['slug'])
            self.stdout.write(self.style.SUCCESS(f'Fixed slug for "{vendor.name}": {slug}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {count} vendor slug(s).'))
