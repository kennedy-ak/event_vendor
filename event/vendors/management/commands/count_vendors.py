from django.core.management.base import BaseCommand
from vendors.models import Vendor
from categories.models import Category


class Command(BaseCommand):
    help = 'Count vendors by category'

    def handle(self, *args, **kwargs):
        total_vendors = Vendor.objects.count()

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'TOTAL VENDORS IN DATABASE: {total_vendors}'))
        self.stdout.write('='*60 + '\n')

        # Count by category
        categories = Category.objects.all()

        self.stdout.write('Vendors by Category:')
        self.stdout.write('-'*60)

        category_total = 0
        for category in categories:
            count = Vendor.objects.filter(category=category).count()
            if count > 0:
                category_total += count
                self.stdout.write(f'  {category.name:<25} : {count:>3} vendors')

        self.stdout.write('-'*60)
        self.stdout.write(f'  {"TOTAL":<25} : {category_total:>3} vendors\n')

        # Count by status
        self.stdout.write('\nVendors by Status:')
        self.stdout.write('-'*60)
        pending = Vendor.objects.filter(status='pending').count()
        active = Vendor.objects.filter(status='active').count()
        suspended = Vendor.objects.filter(status='suspended').count()

        self.stdout.write(f'  Pending   : {pending}')
        self.stdout.write(f'  Active    : {active}')
        self.stdout.write(f'  Suspended : {suspended}')
        self.stdout.write('-'*60 + '\n')
