# 🏋️ PP Kettlebell Bochnia — Live Results

A Django-based web application for managing and publishing results of the **Polish Hardstyle Kettlebell Cup** held in Bochnia, Poland. It lets judges and organizers register athlete performances in real time, automatically compute scores, and stream live rankings to the audience.

![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Django](https://img.shields.io/badge/django-5.2%20LTS-092E20.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📑 Table of contents

- [Features](#-features)
- [Disciplines](#-disciplines)
- [Athlete categories](#-athlete-categories)
- [Tech stack](#-tech-stack)
- [Project structure](#-project-structure)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Database configuration](#-database-configuration)
- [Running the app](#-running-the-app)
- [Admin panel](#-admin-panel)
- [Import / export](#-import--export)
- [Production deployment](#-production-deployment)
- [Security](#-security)
- [Development](#-development)
- [License](#-license)

---

## ✨ Features

- 🔴 **Live results** — updates during the competition, visible to the public
- 📊 **Automatic scoring** — results normalized by athlete body weight (`%BW`)
- 🏆 **Multi-category rankings** — separate leaderboards for each weight class and group
- 🎯 **Multi-discipline events** — Snatch, TGU, See-Saw Press, KB Squat, Pistol Squat
- 📋 **Start list generator** — automated schedule for judges
- 📥 **Import/export** of athlete data (CSV/XLSX) via `django-import-export`
- 🥇 **Special awards** — "Best Bochnia Female" and "Best Bochnia Male" categories
- 🛠️ **Django admin panel** with a judge-friendly station form
- 🔄 **Tie-breaking** via the `tiebreak` flag on `Player`
- 📡 **ASGI support** (Django Channels) — ready for WebSocket live updates

---

## 🎯 Disciplines

| Discipline | Key | Scoring |
|---|---|---|
| Snatch | `snatch` | kettlebell weight × repetitions |
| Turkish Get-Up | `tgu` | max weight / body weight (`%BW`) — 3 attempts |
| One Kettlebell Press | `one_kettlebell_press` | max weight / `%BW` — 3 attempts |
| Kettlebell Squat x2 | `kb_squat_2x` | sum L + R (two bells), 3 attempts |
| Two Kettlebells Press | `two_kettlebell_press` | See-Saw Press L + R × 3, 3 attempts |
| Pistol Squat | — | max weight (special award) |

Each athlete's result is converted to positional points; the sum determines the final ranking within a category (`OverallResult`).

---

## 👥 Athlete categories

The app supports 11 starting categories:

- **Amateur** — Women ≤ 65 kg · Women > 65 kg · Men ≤ 85 kg · Men > 85 kg
- **Pro** — Women · Men ≤ 85 kg · Men > 85 kg
- **Masters** — Women · Men
- **Special awards** — Best Bochnia Female · Best Bochnia Male

Each category has its own set of disciplines (`Category.disciplines`), which makes it easy to tailor the event format.

---

## 🧱 Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 LTS |
| ASGI / realtime | Django Channels 4.x |
| Database (dev) | PostgreSQL (via `pg_service.conf`) |
| Database (prod) | SQLite |
| WSGI server | Gunicorn 23.x |
| Import/export | django-import-export + tablib |
| Frontend | Django templates + vanilla HTML/CSS |
| Code style | Black, isort, autoflake, flake8 |

Full dependency list: [kettlebell_app/requirements.txt](kettlebell_app/requirements.txt)

---

## 📁 Project structure

```
pp_kettlebell_bochnia/
├── LICENSE
├── README.md
└── kettlebell_app/
    ├── manage.py
    ├── requirements.txt
    ├── fixtures/
    │   └── dump.yaml                  # seed data (clubs, categories)
    ├── kettlebell_app/                # Django project package
    │   ├── asgi.py                    # ASGI entrypoint (Channels)
    │   ├── wsgi.py                    # WSGI entrypoint (Gunicorn)
    │   ├── urls.py
    │   ├── settings/
    │   │   ├── base.py                # base settings (PostgreSQL)
    │   │   └── prod.py                # production settings (SQLite)
    │   └── public/                    # collected static files
    └── tournament/                    # main domain app
        ├── models.py                  # Player, Category, *Result, OverallResult
        ├── views.py                   # category views + start list generator
        ├── admin.py                   # judge admin + import/export
        ├── forms.py                   # StationForm (per-station view)
        ├── resources.py               # import/export resources
        ├── urls.py
        ├── migrations/
        ├── templates/                 # one HTML per category
        └── utilities/
            └── csv_find_duplicate.py  # helper script
```

---

## ✅ Requirements

- **Python 3.11+** (3.12 or 3.13 recommended; 3.14 works with `psycopg2-binary>=2.9.10`)
- **PostgreSQL 14+** — for the development environment (SQLite works too)
- **pip** and **venv**
- macOS / Linux (on Windows use WSL2)

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/merynos94/pp_kettlebell_bochnia.git
cd pp_kettlebell_bochnia

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r kettlebell_app/requirements.txt
```

---

## 🗄️ Database configuration

### Option A — PostgreSQL (default in `base.py`)

The base settings use a [PostgreSQL service file](https://www.postgresql.org/docs/current/libpq-pgservice.html). Create `~/.pg_service.conf`:

```ini
[kb_app_service]
host=localhost
port=5432
dbname=kettlebell
user=kettlebell_user
```

and a password file `.my_pgpass` in `kettlebell_app/` (chmod 600):

```
localhost:5432:kettlebell:kettlebell_user:YOUR_PASSWORD
```

### Option B — SQLite (quick start, as in `prod.py`)

Run with production settings (they use SQLite):

```bash
export DJANGO_SETTINGS_MODULE=kettlebell_app.settings.prod
```

or override `DATABASES` in [kettlebell_app/kettlebell_app/settings/base.py](kettlebell_app/kettlebell_app/settings/base.py#L81) to point at SQLite.

### Migrations and seed data

```bash
cd kettlebell_app
python manage.py migrate
python manage.py loaddata fixtures/dump.yaml   # optional
python manage.py createsuperuser
```

---

## ▶️ Running the app

### Development server

```bash
cd kettlebell_app
python manage.py runserver
```

App: http://127.0.0.1:8000/ · Admin: http://127.0.0.1:8000/admin/

### ASGI server (for live updates)

```bash
daphne kettlebell_app.asgi:application
```

---

## 🛠️ Admin panel

The Django admin (`/admin/`) is the main interface for judges. It lets you:

- Create and edit **Players** (`Player`) with the full set of attempt weights
- Manage **Clubs** (`SportClub`) and **Categories** (`Category`) — pick disciplines via checkboxes
- Inspect per-discipline results (`SnatchResult`, `TGUResult`, `SeeSawPressResult`, `KBSquatResult`, `PistolSquatResult`) and overall rankings (`OverallResult`)
- Filter lists by club, category and tie-break flag
- Search athletes by name and club

Results are **recomputed automatically** in `Player.save()` — there is no need to trigger recalculation manually.

---

## 📤 Import / export

`django-import-export` adds **Import** and **Export** buttons for athletes in the admin.

- Supported formats: **CSV**, **XLSX**, **JSON**, **YAML**
- Resources: [kettlebell_app/tournament/resources.py](kettlebell_app/tournament/resources.py) (`PlayerImportResource`, `PlayerExportResource`)
- Duplicate finder: [kettlebell_app/tournament/utilities/csv_find_duplicate.py](kettlebell_app/tournament/utilities/csv_find_duplicate.py)

---

## 🌐 Production deployment

Production settings: [kettlebell_app/kettlebell_app/settings/prod.py](kettlebell_app/kettlebell_app/settings/prod.py)

- `DEBUG = False`
- `ALLOWED_HOSTS = ["ppkettlebell.toadres.pl", "localhost"]`
- Database: SQLite (`db.sqlite3`)
- Static files: `STATIC_ROOT = public/`

### Deploying with Gunicorn

```bash
export DJANGO_SETTINGS_MODULE=kettlebell_app.settings.prod
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn kettlebell_app.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Run Gunicorn behind a reverse proxy (Nginx/Caddy) and terminate TLS there.

> ⚠️ **Before going to production, replace** `SECRET_KEY` in [kettlebell_app/kettlebell_app/settings/prod.py](kettlebell_app/kettlebell_app/settings/prod.py) with a value pulled from an environment variable — never commit secrets to the repository.

---

## 🔒 Security

Dependencies are actively maintained against CVEs:

- **Django 5.2 LTS** — the current LTS branch with full security support
- **sqlparse 0.5.5**, **black 26.5+**, **psycopg2-binary 2.9.10+**
- Repository monitored by **GitHub Dependabot**

To report a vulnerability, use the private **Security Advisory** flow under the repository's Security tab.

### Production security TODO

- [ ] Move `SECRET_KEY` and DB passwords to environment variables (`django-environ`)
- [ ] Enable `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- [ ] Set `SECURE_HSTS_SECONDS`
- [ ] Configure database backups (`DBBACKUP_PATH` is already defined in `prod.py`)

---

## 🧑‍💻 Development

### Formatting and linting

```bash
black kettlebell_app/
isort kettlebell_app/
autoflake --remove-all-unused-imports -r -i kettlebell_app/
flake8 kettlebell_app/
```

### Running tests

```bash
cd kettlebell_app
python manage.py test tournament
```

### Branching convention

- `main` — production branch
- `feature/<name>` — new features
- `fix/<name>` — bug fixes

Pull requests are welcome. Please run `black` and `flake8` before submitting.

---

## 📜 License

Released under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙌 Author

**merynos94** — [github.com/merynos94](https://github.com/merynos94)

Event: **Polish Hardstyle Kettlebell Cup — Bochnia 2024**
