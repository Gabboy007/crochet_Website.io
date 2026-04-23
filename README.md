# Minn Miru Handcrafted

Flask storefront and admin dashboard for Minn Miru Handcrafted.

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

Or on Windows:

```bat
run_app.bat
```

## Production Readiness

This project now supports production-style deployment with environment variables.

Important environment variables:

- `SECRET_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `CONTACT_EMAIL`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`
- `SMTP_SENDER`
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
CONTACT_EMAIL=hello@crochetbloom.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=1
SMTP_SENDER=your-email@gmail.com
```

## Custom Order Email

The custom order form posts to this Flask app at `/custom-order`. To send real emails, set the SMTP environment variables above. For Gmail, use an app password instead of your normal account password.

You can also configure email from the admin dashboard at `/admin/settings`. Dashboard-saved email settings are stored locally in `instance/site_settings.json`, which is ignored by Git so app passwords are not uploaded.

## Run In Production

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with Waitress:

```bash
python serve_prod.py
```

Or on Windows:

```bat
run_prod.bat
```

## Deploy On Vercel

This project includes `index.py` and `vercel.json` so Vercel can run the Flask app as a Python Function.

1. Push the project to GitHub, GitLab, or Bitbucket.
2. In Vercel, choose **Add New Project** and import the repository.
3. Keep the default framework settings. Vercel will install `requirements.txt` and use `index.py`.
4. Add these Environment Variables in the Vercel project settings:

```env
SECRET_KEY=replace-with-a-long-random-secret
ADMIN_USERNAME=your-admin-name
ADMIN_PASSWORD=your-strong-password
FLASK_ENV=production
FLASK_DEBUG=0
TRUST_PROXY=1
SESSION_COOKIE_SECURE=1
DATABASE_URL=postgresql://user:password@host:5432/database
CONTACT_EMAIL=hello@crochetbloom.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=1
SMTP_SENDER=your-email@gmail.com
```

5. Deploy.
6. Run the database migrations against the hosted database before opening the site:

```bash
set DATABASE_URL=postgresql://user:password@host:5432/database
flask --app wsgi db upgrade
```

On macOS/Linux, use `export DATABASE_URL=...` instead of `set DATABASE_URL=...`.

Vercel's filesystem is temporary at runtime, so do not rely on SQLite, dashboard-saved email settings, or uploaded admin images for production persistence. Use a hosted Postgres database through `DATABASE_URL`, and use environment variables for email settings.

If `DATABASE_URL` is not set on Vercel, the app creates a temporary SQLite database so the deployment can boot, but any products, reviews, or uploaded images can disappear when the function instance is replaced. For a real storefront, set `DATABASE_URL` and run migrations.

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
