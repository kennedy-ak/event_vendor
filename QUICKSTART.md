# Quick Start Guide

The application is now configured to use SQLite (no PostgreSQL or PostGIS needed).

## Run These Commands:

```bash
# 1. Navigate to the event directory
cd event

# 2. Create migrations
python manage.py makemigrations

# 3. Apply migrations
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. Seed categories
python manage.py seed_categories

# 6. Seed subscription plans
python manage.py seed_subscription_plans

# 7. Run the development server
python manage.py runserver
```

## Access the Application:

- Homepage: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## What Changed:

- Switched from PostgreSQL + PostGIS to SQLite
- Changed `location` PointField to `latitude` and `longitude` DecimalFields
- Removed GIS dependencies (easier to set up on Windows)

## Next Steps:

1. Create a superuser when prompted
2. Log into admin panel
3. View the seeded categories and subscription plans
4. You can manually create test vendors through the admin panel

Note: Templates are not yet created, so you'll see "TemplateDoesNotExist" errors if you visit the frontend URLs. The admin panel will work perfectly though!
