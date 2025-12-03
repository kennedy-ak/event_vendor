from django.core.management.base import BaseCommand
from django.utils.text import slugify
from categories.models import Category


class Command(BaseCommand):
    help = 'Seed the database with initial event categories'

    def handle(self, *args, **kwargs):
        categories_data = [
            {'name': 'Venues', 'description': 'Event spaces and venues', 'icon': '🏛️'},
            {'name': 'Catering', 'description': 'Food and catering services', 'icon': '🍽️'},
            {'name': 'Photographers', 'description': 'Photography and videography services', 'icon': '📸'},
            {'name': 'DJs', 'description': 'DJ and music services', 'icon': '🎵'},
            {'name': 'Fashion Designers', 'description': 'Fashion design and tailoring', 'icon': '👗'},
            {'name': 'Fabrics', 'description': 'Fabric shops and materials', 'icon': '🧵'},
            {'name': 'Favours', 'description': 'Party favours and gifts', 'icon': '🎁'},
            {'name': 'Drinks', 'description': 'Beverage suppliers', 'icon': '🍹'},
            {'name': 'Event Planners', 'description': 'Professional event planning services', 'icon': '📋'},
            {'name': 'Decorators', 'description': 'Event decoration services', 'icon': '🎈'},
            {'name': 'Florists', 'description': 'Flower arrangements', 'icon': '💐'},
            {'name': 'Entertainment', 'description': 'Live entertainment services', 'icon': '🎭'},
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=slugify(cat_data['name']),
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully seeded {created_count} categories!')
        )
