# BuildCore Construction — Django Website

Isang kumpletong responsive construction-company website na may hiwalay na frontend templates, CSS/JavaScript, at Python Django backend.

## Kasamang features

- Modern, responsive homepage para sa desktop, tablet, at mobile
- About, Services, Projects, Project Detail, Contact, at Privacy pages
- Dynamic services, projects, at testimonials mula sa database
- Project category filtering
- Quotation request form na may validation
- Automatic quotation reference gaya ng `BC-202608-A1B2`
- Automatic customer at company email notification
- Customer quotation-status tracker gamit ang reference + email
- Dated quotation workflow/timeline
- Django Admin para sa projects, services, inquiries, subscribers, at status updates
- Admin quick actions: **Under Review** at **Proposal Sent**
- Contact-message inbox at newsletter subscriber list
- Demo data command para may laman agad ang website
- Automated tests para sa mahahalagang workflow
- SQLite para madaling patakbuhin locally; puwedeng palitan ng PostgreSQL sa production

## Project structure

```text
django_site/
├── manage.py
├── requirements.txt
├── .env.example
├── buildcore/                 # Main Django settings and URLs
├── core/                      # Models, views, forms, workflow, admin, tests
│   ├── management/commands/
│   │   └── seed_demo.py
│   └── migrations/
├── templates/
│   ├── core/                  # Individual HTML pages
│   └── partials/              # Reusable template parts
└── static/core/
    ├── css/style.css          # Lahat ng design at responsive styling
    └── js/main.js             # Mobile menu, animations, copy button, counters
```

## Patakbuhin sa VS Code — Windows PowerShell

1. I-extract ang ZIP at buksan ang `django_site` folder sa VS Code.
2. Buksan ang **Terminal → New Terminal**.
3. Gumawa at i-activate ang virtual environment:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Kung bawal ang script execution sa PowerShell, patakbuhin muna:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Ihanda ang database at demo content:

```powershell
python manage.py migrate
python manage.py seed_demo
```

6. Gumawa ng admin account:

```powershell
python manage.py createsuperuser
```

7. Patakbuhin ang website:

```powershell
python manage.py runserver
```

Buksan:

- Website: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## Quotation workflow

1. Pupunta ang customer sa **Get a free quote**.
2. Iva-validate ng Django ang phone, email, consent, at project description.
3. Kapag valid, mase-save ang request at gagawa ng unique reference number.
4. Gagawa ang system ng unang client-visible status update.
5. Magpapadala ito ng acknowledgment sa customer at notification sa estimator.
6. Sa admin, puwedeng i-assign ang request at baguhin ang status:
   - New request
   - Under review
   - Consultation scheduled
   - Proposal sent
   - Approved
   - Project in progress
   - Completed
   - Closed
7. Bawat status change ay napupunta sa dated timeline.
8. Makikita ng customer ang client-visible updates sa **Track request** gamit ang reference at email.

Ang pangunahing backend functions ay nasa `core/workflows.py`:

- `register_quote_request()` — nagsisimula ng workflow
- `send_quote_notifications()` — customer at estimator emails
- `transition_quote()` — safe status update at timeline logging
- `send_contact_notification()` — notification para sa contact form

## Email setup

Sa local development, lalabas ang emails sa VS Code terminal. Para gumamit ng totoong SMTP:

1. Kopyahin ang `.env.example` at pangalanang `.env`.
2. Palitan ang email values:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=BuildCore Construction <you@example.com>
COMPANY_EMAIL=estimates@example.com
```

Huwag i-upload sa GitHub ang `.env` file.

## Palitan ang company details

- Pangalan, phone, email, address, at office hours: `core/context_processors.py`
- Homepage at page copy: `templates/core/`
- Kulay at visual design: `static/core/css/style.css`, sa `:root` variables
- Demo services/projects/testimonials: `core/management/commands/seed_demo.py`
- External sample images: palitan ang `image_url` sa Django Admin o seed command

Pagkatapos baguhin ang demo seed data, maaari ulit patakbuhin:

```powershell
python manage.py seed_demo
```

Idempotent ito: ia-update nito ang matching demo records at hindi basta-basta magdodoble.

## Tests

```powershell
python manage.py test
python manage.py check
```

Sakop ng tests ang public pages, quotation creation, validation, email workflow, secure tracking, status timeline, contact form, at newsletter deduplication.

## Bago i-deploy

1. Gumawa ng malakas na `DJANGO_SECRET_KEY`.
2. Itakda ang `DJANGO_DEBUG=False`.
3. Ilagay ang actual domain sa `DJANGO_ALLOWED_HOSTS` at `DJANGO_CSRF_TRUSTED_ORIGINS`.
4. Gumamit ng PostgreSQL para sa production kung marami nang users.
5. I-configure ang totoong SMTP email.
6. Palitan ang sample phone, email, address, company claims, privacy copy, at photos.
7. Patakbuhin ang `python manage.py collectstatic --noinput`.

Production server command:

```bash
gunicorn buildcore.wsgi:application
```

## Paalala

Ang business name, contact details, project examples, statistics, certification wording, testimonials, at external photos ay polished demo content. Palitan ang mga ito ng tunay na impormasyon bago gawing public ang website.
