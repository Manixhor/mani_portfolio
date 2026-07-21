# Manikanta Portfolio

Production-ready portfolio with a Django backend for admin-managed content, contact messages, analytics, API endpoints, and the portfolio frontend.

## Project Structure

- `frontend/` - portfolio HTML/CSS/JS served by Django in production
- `backend/` - Django API and admin
- `backend/.env.example` - required production environment variables
- `backend/Procfile` - Gunicorn start command for platforms such as Render/Heroku-style hosts
- `requirements.txt` - Render Python dependency entrypoint
- `build.sh` - Render build command
- `start.sh` - Render start command
- `Procfile` - fallback web start command

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

## Render Deployment

Use one Render web service for the portfolio and one Render PostgreSQL database.

### Option 1: Blueprint

The repository includes `render.yaml` at the repo root. In Render:

1. Go to `Blueprints`.
2. Click `New Blueprint Instance`.
3. Connect this GitHub repository.
4. Render will create the web service and PostgreSQL database.
5. When Render asks for `DJANGO_SUPERUSER_PASSWORD`, enter `portfolio1234`.

The blueprint includes a persistent disk for uploaded admin images. Render disks require a paid web service.

### Option 2: Manual Web Service

If you deploy manually:

```text
Root Directory: portfolio
Runtime: Python 3
Build Command: ./build.sh
Start Command: ./start.sh
Health Check Path: /healthz/
```

`start.sh` runs:

```bash
cd backend
python manage.py migrate --noinput
python manage.py ensure_superuser
gunicorn portfolio_backend.wsgi:application --bind 0.0.0.0:$PORT
```

Required Render variables:

```env
DEBUG=False
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DB_NAME
DJANGO_SUPERUSER_USERNAME=mani
DJANGO_SUPERUSER_EMAIL=manigururam06@gmail.com
DJANGO_SUPERUSER_PASSWORD=portfolio1234
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

Render automatically provides `RENDER_EXTERNAL_HOSTNAME`; the app uses it for `ALLOWED_HOSTS`, CSRF trusted origin, CORS origin, and uploaded image URLs. If you add a custom domain, also set:

```env
ALLOWED_HOSTS=your-custom-domain.com
CORS_ALLOWED_ORIGINS=https://your-custom-domain.com
CSRF_TRUSTED_ORIGINS=https://your-custom-domain.com
PUBLIC_BACKEND_URL=https://your-custom-domain.com
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

Add a persistent disk mounted at:

```text
/opt/render/project/src/backend/media
```

Without a persistent disk, uploaded images can be removed when the service redeploys or restarts.
