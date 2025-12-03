# Ghana Events Marketplace

A discovery and booking platform for event-related services in Ghana. Users can find vendors (venues, caterers, photographers, DJs, fashion designers, etc.) by location and category, view profiles, contact vendors, and manage event planning.

## Features

- **Search & Discovery**: Search vendors by category, keyword, and location
- **Vendor Profiles**: Detailed profiles with media, descriptions, contact info, and reviews
- **Lead Capture**: Contact vendors through "Request Quote" forms
- **Vendor Dashboard**: Vendors can manage listings, view leads, and track analytics
- **Reviews System**: Users can leave reviews and ratings for vendors
- **Admin Panel**: Comprehensive admin interface for managing vendors, leads, and content
- **Subscription Plans**: Basic, Standard, and Premium plans for vendors
- **Featured Listings**: Boost visibility with promoted placements

## Tech Stack

- **Backend**: Django 5.0+
- **Database**: PostgreSQL with PostGIS (for geospatial features)
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Python**: 3.10+

## Project Structure

```
event/
├── accounts/          # User authentication and profiles
├── billing/          # Subscription plans and payments
├── categories/       # Event vendor categories
├── leads/           # Lead/contact requests
├── reviews/         # Vendor reviews and ratings
├── vendors/         # Vendor listings and management
├── event/           # Main Django project settings
├── templates/       # HTML templates (to be created)
├── static/          # Static files (CSS, JS, images)
└── media/           # User-uploaded media files
```

## Setup Instructions

### Prerequisites

1. Python 3.10 or higher
2. PostgreSQL 14+ with PostGIS extension
3. pip or uv package manager

### Installation Steps

#### 1. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

#### 2. Configure PostgreSQL with PostGIS

```bash
# Install PostgreSQL and PostGIS (Windows)
# Download from https://www.postgresql.org/download/windows/
# Download PostGIS from https://postgis.net/install/

# Create database
psql -U postgres
CREATE DATABASE ghana_events_db;
\c ghana_events_db
CREATE EXTENSION postgis;
\q
```

#### 3. Configure Environment Variables

Create a `.env` file in the `event/` directory:

```env
# Database Configuration
DB_ENGINE=django.contrib.gis.db.backends.postgis
DB_NAME=ghana_events_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# For development without PostGIS, you can use SQLite (limited geospatial features)
# DB_ENGINE=django.db.backends.sqlite3
```

#### 4. Run Migrations

```bash
cd event
python manage.py makemigrations
python manage.py migrate
```

#### 5. Create Superuser

```bash
python manage.py createsuperuser
```

#### 6. Seed Initial Data

```bash
# Seed categories
python manage.py seed_categories

# Seed subscription plans
python manage.py seed_subscription_plans
```

#### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

#### 8. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see the application.
Visit `http://localhost:8000/admin` for the admin panel.

## Key Commands

### Database Management

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (WARNING: Deletes all data)
python manage.py flush

# Create database backup
pg_dump -U postgres ghana_events_db > backup.sql

# Restore database
psql -U postgres ghana_events_db < backup.sql
```

### Data Management

```bash
# Seed categories
python manage.py seed_categories

# Seed subscription plans
python manage.py seed_subscription_plans

# Create superuser
python manage.py createsuperuser

# Load data from JSON fixtures
python manage.py loaddata fixture_name.json

# Export data to JSON
python manage.py dumpdata app_name.ModelName --indent 2 > fixture.json
```

### Development

```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000

# Open Django shell
python manage.py shell

# Create new app
python manage.py startapp app_name
```

### Static Files

```bash
# Collect static files
python manage.py collectstatic

# Collect static files without prompts
python manage.py collectstatic --noinput

# Clear collected static files
python manage.py collectstatic --clear
```

### Testing

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts

# Run with verbosity
python manage.py test --verbosity 2

# Run with coverage (if installed)
coverage run --source='.' manage.py test
coverage report
```

## User Roles

1. **Guest**: Browse vendors, view profiles, limited contact info
2. **Registered User**: Save favorites, request quotes, leave reviews
3. **Vendor**: Manage profile, upload media, view leads, track analytics
4. **Admin**: Manage all users, vendors, content, and billing

## API Endpoints (Traditional Django Views)

- `/` - Homepage with categories and featured vendors
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/profile/` - User profile management
- `/accounts/favorites/` - User's favorite vendors
- `/vendors/` - List all vendors
- `/vendors/category/<slug>/` - Vendors by category
- `/vendors/<slug>/` - Vendor detail page
- `/vendors/create/` - Create new vendor listing (vendors only)
- `/vendors/<slug>/edit/` - Edit vendor listing
- `/vendors/dashboard/` - Vendor dashboard
- `/leads/contact/<vendor_slug>/` - Create lead/contact request
- `/leads/` - View all leads (vendors only)
- `/reviews/add/<vendor_slug>/` - Add review
- `/reviews/<id>/edit/` - Edit review
- `/reviews/<id>/delete/` - Delete review

## Next Steps

### Phase 1 - Templates (Current)
- Create base template with Bootstrap 5
- Create homepage template
- Create vendor listing templates
- Create vendor dashboard templates
- Create auth templates

### Phase 2 - Enhanced Features
- Add image upload functionality
- Implement payment gateway integration (Paystack/Flutterwave)
- Add email notifications for leads
- Implement SMS notifications

### Phase 3 - Advanced Features
- Add booking calendar
- Implement in-app messaging
- Add geospatial search with maps
- Multi-city support
- Analytics dashboard

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team.
