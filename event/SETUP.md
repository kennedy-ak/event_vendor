# Ghana Events Marketplace - Setup Guide

Complete setup guide for the Ghana Events Marketplace platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Payment Gateway Setup](#payment-gateway-setup)
6. [Email Configuration](#email-configuration)
7. [Cloud Storage Setup](#cloud-storage-setup)
8. [Running the Application](#running-the-application)
9. [Creating Superuser](#creating-superuser)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- PostgreSQL 12+ with PostGIS extension (for production)
- A Paystack account (for payments)

---

## Installation

### 1. Clone the repository
```bash
cd C:\Users\User2\Desktop\event_vendor\event
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Create environment file
```bash
cp .env.example .env
```

### 2. Edit .env file
Open `.env` and configure the following:

#### Django Settings
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

**Generate a new SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Site Configuration
```env
SITE_URL=http://localhost:8000
SITE_NAME=Ghana Events Marketplace
```

---

## Database Setup

### Option 1: SQLite (Development - Default)
No additional configuration needed. Django will create `db.sqlite3` automatically.

### Option 2: PostgreSQL with PostGIS (Production)

#### Install PostGIS
**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib postgis
```

**macOS:**
```bash
brew install postgresql postgis
```

#### Create Database
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE ghana_events_db;
CREATE USER ghana_events_user WITH PASSWORD 'your-password';
ALTER ROLE ghana_events_user SET client_encoding TO 'utf8';
ALTER ROLE ghana_events_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ghana_events_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ghana_events_db TO ghana_events_user;

-- Enable PostGIS extension
\c ghana_events_db
CREATE EXTENSION postgis;
```

#### Update settings.py
Uncomment the PostgreSQL configuration in `event/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ghana_events_db',
        'USER': 'ghana_events_user',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Also uncomment in INSTALLED_APPS:
```python
'django.contrib.gis',  # Uncomment this line
```

---

## Payment Gateway Setup

### Paystack Configuration

1. **Create a Paystack account**
   - Go to [https://paystack.com](https://paystack.com)
   - Sign up for an account
   - Verify your email

2. **Get API Keys**
   - Login to Paystack Dashboard
   - Go to Settings ’ API Keys & Webhooks
   - Copy your Test Public Key and Test Secret Key

3. **Update .env file**
```env
PAYSTACK_PUBLIC_KEY=pk_test_your_public_key_here
PAYSTACK_SECRET_KEY=sk_test_your_secret_key_here
```

4. **Configure Webhook**
   - In Paystack Dashboard, go to Settings ’ API Keys & Webhooks
   - Add webhook URL: `https://your-domain.com/billing/webhook/paystack/`
   - This receives payment notifications

---

## Email Configuration

### Option 1: Console Backend (Development)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Emails will be printed to console.

### Option 2: Gmail SMTP
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Ghana Events <noreply@ghanaevents.com>
```

**Get Gmail App Password:**
1. Go to Google Account settings
2. Security ’ 2-Step Verification
3. App passwords ’ Generate password
4. Use generated password in EMAIL_HOST_PASSWORD

### Option 3: SendGrid
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

---

## Cloud Storage Setup

### Option 1: Local Storage (Development - Default)
```env
USE_S3=False
```
Images will be stored in `media/` folder.

### Option 2: AWS S3
```env
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

**Setup AWS S3:**
1. Create an S3 bucket
2. Set bucket policy to allow public read access
3. Create IAM user with S3 permissions
4. Generate access keys

### Option 3: DigitalOcean Spaces
```env
USE_S3=True
AWS_ACCESS_KEY_ID=your-spaces-key
AWS_SECRET_ACCESS_KEY=your-spaces-secret
AWS_STORAGE_BUCKET_NAME=your-space-name
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_CUSTOM_DOMAIN=your-space.nyc3.digitaloceanspaces.com
```

---

## Running the Application

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```
Follow prompts to create admin account.

### 3. Create Subscription Plans
```bash
python manage.py shell
```

```python
from billing.models import SubscriptionPlan

# Basic Plan
SubscriptionPlan.objects.create(
    name='basic',
    display_name='Basic Plan',
    description='Essential features for small businesses',
    price=50.00,
    currency='GHS',
    features=['Basic listing', 'Contact form', 'Basic analytics', '5 images'],
    max_images=5,
    max_leads_per_month=20,
    featured_listing_included=False,
    is_active=True
)

# Standard Plan
SubscriptionPlan.objects.create(
    name='standard',
    display_name='Standard Plan',
    description='Perfect for growing businesses',
    price=150.00,
    currency='GHS',
    features=['Priority listing', 'Advanced analytics', 'Email support', '15 images', '1 featured listing/month'],
    max_images=15,
    max_leads_per_month=100,
    featured_listing_included=True,
    is_active=True
)

# Premium Plan
SubscriptionPlan.objects.create(
    name='premium',
    display_name='Premium Plan',
    description='Maximum visibility and unlimited features',
    price=300.00,
    currency='GHS',
    features=['Top placement', 'Unlimited images', 'Unlimited leads', 'Priority support', 'Unlimited featured listings'],
    max_images=None,  # Unlimited
    max_leads_per_month=None,  # Unlimited
    featured_listing_included=True,
    is_active=True
)
```

### 4. Create Categories
```python
from categories.models import Category

categories = [
    {'name': 'Venues', 'icon': 'building'},
    {'name': 'Catering', 'icon': 'cup-hot'},
    {'name': 'Photography', 'icon': 'camera'},
    {'name': 'DJ & Entertainment', 'icon': 'music-note-beamed'},
    {'name': 'Fashion & Styling', 'icon': 'scissors'},
    {'name': 'Fabrics', 'icon': 'palette'},
    {'name': 'Party Favours', 'icon': 'gift'},
    {'name': 'Drinks', 'icon': 'cup-straw'},
    {'name': 'Event Planning', 'icon': 'calendar-event'},
]

for cat in categories:
    Category.objects.get_or_create(
        name=cat['name'],
        defaults={'icon': cat['icon']}
    )
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

---

## Creating Superuser

### Access Admin Panel
1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. You can manage:
   - Users
   - Vendors
   - Categories
   - Subscriptions
   - Leads
   - Reviews

---

## Production Deployment

### 1. Set Environment Variables
```env
DEBUG=False
ALLOWED_HOSTS=your-production-domain.com
USE_S3=True
```

### 2. Use Gunicorn
```bash
pip install gunicorn
gunicorn event.wsgi:application --bind 0.0.0.0:8000
```

### 3. Use Nginx as Reverse Proxy
Create `/etc/nginx/sites-available/ghana-events`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /path/to/event/staticfiles/;
    }

    location /media/ {
        alias /path/to/event/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL Certificate (Let's Encrypt)
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Make sure virtual environment is activated and all dependencies are installed.
```bash
pip install -r requirements.txt
```

### Issue: Database Connection Error
**Solution:** Check PostgreSQL is running and credentials are correct.
```bash
sudo systemctl status postgresql
```

### Issue: Paystack Payments Not Working
**Solution:**
1. Check API keys are correct (test keys for development)
2. Verify webhook URL is accessible
3. Check Paystack dashboard for errors

### Issue: Images Not Uploading
**Solution:**
1. Check `media/` folder has write permissions
2. If using S3, verify bucket permissions
3. Check `MEDIA_ROOT` and `MEDIA_URL` settings

### Issue: Emails Not Sending
**Solution:**
1. Check email backend configuration
2. Verify SMTP credentials
3. Check spam folder
4. Use console backend for testing

---

## Color Palette (Design Reference)

The application uses an ocean-inspired color theme:

- **Deep Navy:** `#03045E`
- **Royal Blue:** `#0077B6`
- **Ocean Blue:** `#00B4D8`
- **Light Aqua:** `#90E0EF`
- **Pale Cyan:** `#CAF0F8`

---

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Email: support@ghanaevents.com

---

## License

[Your License Here]
