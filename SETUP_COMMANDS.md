# Ghana Events Marketplace - Setup Commands

## All commands to run to get started

Copy and paste these commands in order. Run them from the project root directory.

### 1. Install Dependencies

```bash
cd event
pip install django psycopg2-binary pillow django-crispy-forms crispy-bootstrap5 python-dotenv
```

Or using the pyproject.toml:

```bash
pip install -e .
```

### 2. Set Up PostgreSQL Database

**Option A: With PostgreSQL + PostGIS (Recommended for production)**

```bash
# First, install PostgreSQL and PostGIS on your system
# Then create the database:
```

```sql
-- Run these in psql or pgAdmin
CREATE DATABASE ghana_events_db;
\c ghana_events_db
CREATE EXTENSION postgis;
```

**Option B: Use SQLite for quick development (No geospatial features)**

Edit `event/event/settings.py` and uncomment the SQLite database configuration.

### 3. Create Environment File

```bash
# Copy the example env file
cp event/.env.example event/.env

# Edit .env and update your database password and secret key
```

### 4. Run Database Migrations

```bash
cd event
python manage.py makemigrations accounts
python manage.py makemigrations categories
python manage.py makemigrations vendors
python manage.py makemigrations leads
python manage.py makemigrations billing
python manage.py makemigrations reviews
python manage.py migrate
```

### 5. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 6. Seed Initial Data

```bash
# Seed categories (venues, catering, photographers, etc.)
python manage.py seed_categories

# Seed subscription plans (basic, standard, premium)
python manage.py seed_subscription_plans
```

### 7. Create Media and Static Directories

```bash
# Windows
mkdir media
mkdir staticfiles

# Linux/Mac
mkdir -p media staticfiles
```

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Run the Development Server

```bash
python manage.py runserver
```

### 10. Access the Application

- **Homepage**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Login with the superuser account you created**

---

## Quick Start (All Commands Together)

### Windows (Command Prompt or PowerShell)

```bash
cd event
pip install django psycopg2-binary pillow django-crispy-forms crispy-bootstrap5 python-dotenv
copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_categories
python manage.py seed_subscription_plans
mkdir media
mkdir staticfiles
python manage.py collectstatic --noinput
python manage.py runserver
```

### Linux/Mac (Bash)

```bash
cd event
pip install django psycopg2-binary pillow django-crispy-forms crispy-bootstrap5 python-dotenv
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_categories
python manage.py seed_subscription_plans
mkdir -p media staticfiles
python manage.py collectstatic --noinput
python manage.py runserver
```

---

## Troubleshooting

### PostGIS Installation Issues

If you have trouble with PostGIS:

1. Edit `event/event/settings.py`
2. Find the DATABASES configuration
3. Comment out the PostGIS configuration
4. Uncomment the SQLite configuration
5. In `vendors/models.py`, comment out the `location` field or change it to regular CharField

### Migration Issues

If you get migration errors:

```bash
# Delete all migration files (except __init__.py)
# Then run:
python manage.py makemigrations
python manage.py migrate
```

### "No module named" Errors

Make sure all dependencies are installed:

```bash
pip install -e .
```

Or install individually:

```bash
pip install django psycopg2-binary pillow django-crispy-forms crispy-bootstrap5 python-dotenv
```

---

## Next Steps After Setup

1. **Log into Admin Panel**: http://localhost:8000/admin
2. **Approve Categories**: Check that categories were created
3. **Create Test Vendor**:
   - Register as a vendor at `/accounts/register/`
   - Create a vendor listing at `/vendors/create/`
   - Approve it in the admin panel
4. **Test the Application**: Browse vendors, create leads, add reviews

---

## Development Workflow

### Daily Development

```bash
cd event
python manage.py runserver
```

### After Model Changes

```bash
python manage.py makemigrations
python manage.py migrate
```

### Reset Database (Warning: Deletes all data)

```bash
python manage.py flush
python manage.py seed_categories
python manage.py seed_subscription_plans
python manage.py createsuperuser
```

---

## Production Deployment Commands

```bash
# Set environment variables
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com
export SECRET_KEY=your-production-secret-key

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Use gunicorn or uwsgi for production
gunicorn event.wsgi:application --bind 0.0.0.0:8000
```

