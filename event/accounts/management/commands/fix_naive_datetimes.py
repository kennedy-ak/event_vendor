from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
import django.apps


class Command(BaseCommand):
    help = 'Fix naive datetime warnings by making all datetime fields timezone-aware'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to fix naive datetime fields...')
        
        # Get all models from installed apps
        apps = django.apps.apps.get_app_configs()
        
        total_fixed = 0
        
        for app in apps:
            # Skip Django's built-in apps
            if app.name.startswith('django.'):
                continue
                
            self.stdout.write(f'\nProcessing app: {app.name}')
            
            for model in app.get_models():
                # Get all DateTimeField fields in the model
                datetime_fields = [
                    field.name for field in model._meta.get_fields()
                    if isinstance(field, models.DateTimeField)
                ]
                
                if not datetime_fields:
                    continue
                
                model_name = model.__name__
                self.stdout.write(f'  Checking {model_name}...')
                
                # Get all records for this model
                queryset = model.objects.all()
                count = queryset.count()
                
                if count == 0:
                    continue
                
                # Check each record for naive datetimes
                for obj in queryset:
                    updated = False
                    for field_name in datetime_fields:
                        value = getattr(obj, field_name)
                        if value is not None and timezone.is_naive(value):
                            # Make the datetime timezone-aware
                            setattr(obj, field_name, timezone.make_aware(value, timezone.get_current_timezone()))
                            updated = True
                    
                    if updated:
                        obj.save()
                        total_fixed += 1
                
                self.stdout.write(f'    Fixed {total_fixed} records in {model_name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully fixed {total_fixed} datetime fields!'))
