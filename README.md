# Crochet Bloom

Flask storefront and admin dashboard for Crochet Bloom.

## Local Development

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python run.py
```

## Production Readiness

This project now supports production-style deployment with environment variables.

Important environment variables:

- `SECRET_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `DATABASE_URL`
- `HOST`
- `PORT`
- `FLASK_ENV`
- `FLASK_DEBUG`
- `TRUST_PROXY`
- `SESSION_COOKIE_SECURE`
- `SERVER_NAME`

Recommended production values:

```env
SECRET_KEY=replace-with-a-long-random-secret
ADMIN_USERNAME=your-admin-name
ADMIN_PASSWORD=your-strong-password
FLASK_ENV=production
FLASK_DEBUG=0
TRUST_PROXY=1
SESSION_COOKIE_SECURE=1
PORT=8080
```

## Run In Production

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with Waitress:

```bash
python serve_prod.py
```

## Domain Setup

Typical setup for a real domain:

1. Point your domain DNS to your server.
2. Run this Flask app behind a reverse proxy such as Nginx, Caddy, or a hosting platform.
3. Terminate HTTPS at the reverse proxy.
4. Forward requests to the app on the port you set, for example `8080`.
5. Set `TRUST_PROXY=1` when using a reverse proxy.

## Notes

- Do not use the default admin credentials on a public site.
- Do not use the development server for public traffic.
- Uploaded images are stored in `app/static/uploads`, so make sure that folder persists on your host.
