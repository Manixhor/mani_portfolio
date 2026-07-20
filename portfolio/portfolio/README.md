# Manikanta Portfolio

Production-ready portfolio with a Django backend for admin-managed content, contact messages, analytics, API endpoints, and the portfolio frontend.

## Project Structure

- `frontend/` - portfolio HTML/CSS/JS served by Django in production
- `backend/` - Django API and admin
- `backend/.env.example` - required production environment variables
- `backend/Procfile` - Gunicorn start command for platforms such as Render/Heroku-style hosts
- `requirements.txt` - Northflank buildpack dependency entrypoint
- `Procfile` - Northflank buildpack start command

## Local Development

Backend:

```bash
cd portfolio/backend
../../venv/bin/python manage.py migrate
../../venv/bin/python manage.py createsuperuser
../../venv/bin/python manage.py runserver
```

Frontend:

```bash
cd portfolio/frontend
python3 -m http.server 5500
```

Open:

- Frontend: `http://127.0.0.1:5500`
- Backend: `http://127.0.0.1:8000`
- Admin: `http://127.0.0.1:8000/admin/`
- Health check: `http://127.0.0.1:8000/healthz/`

## Production Checklist

1. Copy `backend/.env.example` to your hosting environment variables.
2. Set a strong `SECRET_KEY`.
3. Set `DEBUG=False`.
4. Set `ALLOWED_HOSTS` to your backend domain.
5. Set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to your frontend domain.
6. Set `DATABASE_URL` to a production PostgreSQL database.
7. Run migrations:

```bash
python manage.py migrate
```

8. Collect static files:

```bash
python manage.py collectstatic --noinput
```

9. Start with Gunicorn:

```bash
gunicorn portfolio_backend.wsgi:application
```

## Useful API Routes

- `GET /healthz/`
- `GET /api/portfolio/config/`
- `POST /api/contact/submit/`
- `POST /api/analytics/track/`
- `GET /admin/`

## Northflank Deployment Without Docker

Use one Northflank combined service for this project.

Build settings:

```text
Build type: Buildpack
Build context: /portfolio
Port: 8000
Protocol: HTTP
Public: enabled
Health check path: /healthz/
```

Runtime command is already in `Procfile`:

```bash
cd backend && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn portfolio_backend.wsgi:application --bind 0.0.0.0:$PORT
```

Required Northflank variables:

```env
DEBUG=False
SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_HOSTS=your-service.code.run,your-custom-domain.com
CORS_ALLOWED_ORIGINS=https://your-service.code.run,https://your-custom-domain.com
CSRF_TRUSTED_ORIGINS=https://your-service.code.run,https://your-custom-domain.com
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DB_NAME
PUBLIC_BACKEND_URL=https://your-service.code.run
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

Contact form email variables:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
CONTACT_NOTIFICATION_EMAIL=your-email@gmail.com
```

Admin image uploads:

Add a persistent volume mounted at:

```text
/app/backend/media
```

Without a persistent volume, uploaded images can be removed when the container is redeployed.
