# Deploy Django Digital Forensic Security App (Free - PythonAnywhere)

This guide deploys your Django app on **PythonAnywhere** (free tier) with SQLite, static files, and HTTPS.

---

## Why PythonAnywhere?

- **Free** – No credit card required
- **SQLite** – Persistent database (unlike Render/Railway free tiers)
- **Django** – Native Python/Django support
- **HTTPS** – Free SSL on `*.pythonanywhere.com`

---

## Prerequisites

- PythonAnywhere account: [pythonanywhere.com/registration](https://www.pythonanywhere.com/registration)
- GitHub account (optional but recommended)

---

## Step 1: Push Project to GitHub

```bash
cd "d:\Final Year Project\Final Project\forensic"

# Initialize git if not done
git init
git add .
git commit -m "Initial commit for deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create PythonAnywhere Account & Web App

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com) and register (free).
2. Open **Dashboard** → **Web** → **Add a new web app**.
3. Choose **Manual configuration** (not Django wizard).
4. Select **Python 3.10** (or 3.11 if available).
5. Click **Next** and finish.

---

## Step 3: Clone Project & Set Up Virtual Environment

Open a **Bash console** on PythonAnywhere:

```bash
# Clone your repo (replace with your repo URL)
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git forensic

# Create virtual environment
cd forensic
python3 -m venv venv
source venv/bin/activate   # Linux/Mac on PA

# Install dependencies
pip install -r requirements.txt
```

---

## Step 4: Configure Web App

In the **Web** tab:

### 4.1 Code

- **Source code**: `/home/YOUR_USERNAME/forensic`
- **Working directory**: `/home/YOUR_USERNAME/forensic`
- **WSGI configuration file**: Click the link, replace contents with:

```python
# /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py

import os
import sys

# Production settings (REQUIRED)
os.environ['DJANGO_DEBUG'] = '0'
os.environ['DJANGO_SECRET_KEY'] = 'CHANGE-THIS-TO-A-SECURE-RANDOM-STRING-50-CHARS'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'YOUR_USERNAME.pythonanywhere.com,.pythonanywhere.com'

path = '/home/YOUR_USERNAME/forensic'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ImprovingDigitalForensicSecurity.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace `YOUR_USERNAME` everywhere. Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4.2 Virtualenv

- **Virtualenv**: `/home/nazeebshaik/forensic/venv`

### 4.3 Static Files

Add mappings:

| URL          | Directory                               |
|--------------|-----------------------------------------|
| /static/     | /home/nazeebshaik/forensic/staticfiles |
| /media/      | /home/nazeebshaik/forensic/media      |

---

## Step 5: Run Migrations & Collect Static Files

In the Bash console:

```bash
cd ~/forensic
source venv/bin/activate

# Migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser for Django admin (optional)
python manage.py createsuperuser
```

---

## Step 6: Reload Web App

In the **Web** tab, click **Reload YOUR_USERNAME.pythonanywhere.com**.

---

## Live URLs

| Link           | URL                                             |
|----------------|--------------------------------------------------|
| **Website**    | `https://YOUR_USERNAME.pythonanywhere.com`       |
| **Admin panel**| `https://YOUR_USERNAME.pythonanywhere.com/admin/`|

---

## Updating the Site After Code Changes

```bash
# In Bash console
cd ~/forensic
git pull origin main

source venv/bin/activate
pip install -r requirements.txt   # if requirements changed
python manage.py migrate          # if models changed
python manage.py collectstatic --noinput
```

Then **Reload** your web app in the Web tab.

---

## Security Notes

- Email credentials in `settings.py` are hardcoded. For production, use environment variables or PythonAnywhere "Environment Variables" (paid feature). Free tier: consider a separate config module.
- PythonAnywhere free tier restricts outbound SMTP. Email may fail; test after deploy.

---

## Troubleshooting

| Issue            | Fix                                                                 |
|------------------|---------------------------------------------------------------------|
| 500 error        | Check **Error log** in Web tab. Often WSGI path or imports wrong.   |
| Static not loading | Run `collectstatic`, check Static files mappings.                  |
| CSRF / 403       | Ensure `CSRF_TRUSTED_ORIGINS` includes `https://*.pythonanywhere.com` |
| Module not found | Activate venv in WSGI or add `sys.path` in WSGI file.              |

---

## Summary

- **Platform**: PythonAnywhere free tier  
- **Database**: SQLite (persistent)  
- **Static**: WhiteNoise + static file mappings  
- **HTTPS**: Built-in on PythonAnywhere subdomains  
