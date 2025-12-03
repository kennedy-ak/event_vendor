from django.core.management.base import BaseCommand
from billing.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Seed the database with subscription plans'

    def handle(self, *args, **kwargs):
        plans_data = [
            {
                'name': 'basic',
                'display_name': 'Basic Plan',
                'description': 'Perfect for getting started',
                'price': 50.00,
                'features': [
                    'Basic listing',
                    'Up to 5 images',
                    'Contact information displayed',
                    'Basic analytics'
                ],
                'max_images': 5,
                'max_leads_per_month': 20,
                'featured_listing_included': False,
            },
            {
                'name': 'standard',
                'display_name': 'Standard Plan',
                'description': 'Most popular for growing businesses',
                'price': 150.00,
                'features': [
                    'Premium listing',
                    'Up to 15 images',
                    'Priority in search results',
                    'Advanced analytics',
                    '1 featured listing per month'
                ],
                'max_images': 15,
                'max_leads_per_month': 100,
                'featured_listing_included': True,
            },
            {
                'name': 'premium',
                'display_name': 'Premium Plan',
                'description': 'For established vendors',
                'price': 300.00,
                'features': [
                    'Featured listing',
                    'Unlimited images',
                    'Top placement in search',
                    'Comprehensive analytics',
                    'Unlimited featured listings',
                    'Priority customer support',
                    'Social media promotion'
                ],
                'max_images': 50,
                'max_leads_per_month': None,  # Unlimited
                'featured_listing_included': True,
            },
        ]

        created_count = 0
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.display_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully seeded {created_count} subscription plans!')
        )
