# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ghana Events Marketplace is a Django-based platform for discovering and booking event service vendors in Ghana. Users can find vendors (venues, caterers, photographers, DJs, etc.) by location and category, view profiles, and contact vendors through a lead generation system.

**Tech Stack:**
- Backend: Django 5.0+
- Database: SQLite (dev), PostgreSQL + PostGIS (production)
- Frontend: Bootstrap 5 with Crispy Forms
- AI: OpenAI GPT-4 for event planning chatbot
- Payments: Paystack
- Storage: AWS S3/DigitalOcean Spaces (production)

## Essential Commands

**Development Server:**
```bash
cd event  # The inner event/ directory contains manage.py
python manage.py runserver
```

**Database Operations:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

**Data Seeding:**
```bash
python manage.py seed_categories
python manage.py seed_subscription_plans
```

**Static Files:**
```bash
python manage.py collectstatic --noinput
```

**Testing:**
```bash
python manage.py test                    # All tests
python manage.py test accounts           # Specific app
python manage.py test --verbosity 2      # Verbose output
```

**Django Shell:**
```bash
python manage.py shell
```

## Project Structure

```
event/
├── event/                # Django project settings (settings.py, urls.py, wsgi.py)
├── accounts/             # Custom user model, authentication, profiles
├── categories/           # Event vendor categorization system
├── vendors/              # Core vendor listings, search, profiles
├── leads/                # Lead/contact request management
├── reviews/              # Vendor reviews and rating system
├── billing/              # Subscription plans, payments, Paystack integration
├── chatbot/              # AI-powered event planning assistant (OpenAI)
├── templates/            # Global HTML templates (Bootstrap 5)
├── static/               # CSS, JS, images
├── media/                # User-uploaded content
└── manage.py             # Django management script
```

**Important:** The project has a nested directory structure. The root `event/` folder contains `manage.py` and the inner `event/` folder contains settings.

## Architecture & Key Patterns

### Custom User Model
- Uses UUID-based primary keys (`accounts.User`)
- Email-based authentication (not username)
- Role-based access: Guest, Registered User, Vendor, Admin
- Custom user model: `AUTH_USER_MODEL = 'accounts.User'`

### Vendor System
- `Vendor` model has rich profiles with images, pricing, location, ratings
- Categories with icons (Venues, Catering, Photography, DJ & Entertainment, Fashion & Styling, etc.)
- Geospatial features: location-based search (requires PostGIS in production)
- Vendor dashboard for analytics and lead management

### Marketplace Flow
1. Users browse/search vendors by category, location, price, rating
2. View detailed vendor profiles
3. Submit lead/contact requests through forms
4. Vendors receive leads and can respond
5. Users can leave reviews and ratings

### Subscription & Billing
- Three tiers: Basic, Standard, Premium
- Paystack payment gateway integration
- Featured listings (boosts) for visibility
- Webhook handling for payment confirmation

### AI Chatbot
- Conversational event planning assistant using OpenAI GPT-4
- Collects event requirements (type, date, budget, location, guest count)
- Generates vendor recommendations from database
- Tracks analytics (views, contacts, favorites)
- Email export for recommendations

## Configuration Files

### `.env` (Environment Variables)
Essential variables to configure:
```env
SECRET_KEY=                    # Django secret key
DEBUG=True                     # False in production
ALLOWED_HOSTS=                 # Comma-separated domains
OPENAI_API_KEY=                # For AI chatbot
PAYSTACK_PUBLIC_KEY=           # Paystack payments
PAYSTACK_SECRET_KEY=
USE_S3=False                   # True for cloud storage
EMAIL_BACKEND=                 # SMTP for notifications
```

### Database Configuration
- **Development:** SQLite (default) - no setup required
- **Production:** PostgreSQL + PostGIS (commented out in settings.py)
  - To enable, uncomment PostGIS DATABASES config and add `django.contrib.gis` to INSTALLED_APPS

## Key Views & URL Patterns

- `/` - Homepage with categories and featured vendors
- `/accounts/` - Registration, login, profile management
- `/vendors/` - Vendor listings, search, detail pages
- `/leads/` - Contact forms and lead management
- `/billing/` - Subscription plans and payments
- `/chatbot/` - AI event planning assistant
- `/admin/` - Django admin panel

## Custom Management Commands

- `seed_categories` - Populates Category model with initial event categories
- `seed_subscription_plans` - Creates Basic/Standard/Premium subscription tiers

## Frontend Architecture

- **Bootstrap 5** via `crispy-bootstrap5`
- Base template at `templates/base.html`
- Crispy Forms for form rendering
- Ocean-inspired color theme:
  - Deep Navy: `#03045E`
  - Royal Blue: `#0077B6`
  - Ocean Blue: `#00B4D8`
  - Light Aqua: `#90E0EF`
  - Pale Cyan: `#CAF0F8`

## Development Notes

1. **Working Directory:** Always run commands from the inner `event/` directory (where `manage.py` is located)

2. **Migrations:** After model changes, always run `makemigrations` then `migrate`

3. **Static Files:** Run `collectstatic --noinput` after adding CSS/JS changes in production

4. **Geospatial Features:** Full PostGIS support is disabled in development (SQLite backend). To test location-based search, enable PostGIS in settings.

5. **CORS/CSRF:** The project is configured for frontend integration with trusted origins. When adding new frontend domains, update:
   - `CORS_ALLOWED_ORIGINS` in settings.py
   - `CSRF_TRUSTED_ORIGINS` in settings.py

6. **Email:** Uses console backend by default (prints to terminal). Configure SMTP in `.env` for real emails.

7. **Media Storage:** Uses local `media/` folder in development. Set `USE_S3=True` for cloud storage in production.

## Production Deployment

- Use `gunicorn` as WSGI server: `gunicorn event.wsgi:application`
- WhiteNoise serves static files (no nginx required for static assets)
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`
- Configure PostgreSQL + PostGIS database
- Set up cloud storage (AWS S3 or DigitalOcean Spaces)
- Configure Paystack webhook URL: `https://your-domain.com/billing/webhook/paystack/`
