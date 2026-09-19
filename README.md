# Attendance Management System

A Django REST Framework project for managing departments, members, and attendance records with role-based access control.

## Overview

This application provides:
- user registration and role management
- department and staff/member records
- attendance marking for members
- staff-only bulk attendance updates
- attendance summaries and CSV export
- PostgreSQL-ready configuration

## Tech Stack

- Python 3.12+
- Django 6.1+
- Django REST Framework
- PostgreSQL
- django-filter
- djangorestframework-simplejwt

## Project Structure

```text
Attendance-Management-System/
├── accounts/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── attendance/
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── people/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── .gitignore
├── LICENSE
├── manage.py
├── README.md
└── requirements.txt
```

## Prerequisites

Before running the app, ensure the following are installed:
- Python 3.12+
- PostgreSQL 14+ (or compatible local instance)
- `pip` and `virtualenv` or `venv`
- Git

## Local Setup

1. Clone the repository

```bash
git clone <repository-url>
cd Attendance-Management-System
```

2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not present, install the project dependencies explicitly:

```bash
pip install Django djangorestframework djangorestframework-simplejwt django-filter psycopg[binary]
```

4. Create a PostgreSQL database

```bash
createdb attendance_management
```

Or with `psql`:

```bash
psql -U postgres
CREATE DATABASE attendance_management;
```

5. Configure environment variables

Create a `.env` file in the project root:

```env
USE_POSTGRES=true
POSTGRES_DB=attendance_management
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=your-long-random-secret-key
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Then export them in your shell if needed:

```bash
export USE_POSTGRES=true
export POSTGRES_DB=attendance_management
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password_here
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export DJANGO_SECRET_KEY='your-long-random-secret-key'
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

`DJANGO_SECRET_KEY` is required and must contain at least 50 characters. Generate
one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

6. Run database migrations

```bash
python manage.py migrate
```

7. Create a superuser (optional but recommended)

```bash
python manage.py createsuperuser
```

8. Start the development server

```bash
python manage.py runserver
```

## Authentication and Authorization

The project uses JWT authentication via `djangorestframework-simplejwt`.

Access tokens expire after 5 minutes. Refresh tokens expire after 1 day, are
rotated on use, and are blacklisted after rotation. After enabling the token
blacklist app, apply its database migrations before using refresh-token
rotation:

```bash
python manage.py migrate
```

## Frontend

The responsive React dashboard lives in `frontend/` and connects to the API
at `http://localhost:8000/api` by default. To run it locally, install Node.js
18 or newer, then run:

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` in `frontend/.env` if the API runs at another URL. The
Django API allows the Vite development origin through `CORS_ALLOWED_ORIGINS`.

Available auth endpoints:
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

Role-based access:
- `admin`
- `teacher_hr`
- `member`

Permissions are enforced through custom permission classes in `accounts/permissions.py`.

## API Endpoints

### Departments
- `GET /api/departments/`
- `POST /api/departments/`
- `GET /api/departments/<id>/`
- `PUT /api/departments/<id>/`
- `PATCH /api/departments/<id>/`
- `DELETE /api/departments/<id>/`

### Members
- `GET /api/members/`
- `POST /api/members/`
- `GET /api/members/<id>/`
- `PUT /api/members/<id>/`
- `PATCH /api/members/<id>/`
- `DELETE /api/members/<id>/`

### Attendance
- `GET /api/attendance/`
- `POST /api/attendance/`
- `GET /api/attendance/<id>/`
- `PUT /api/attendance/<id>/`
- `PATCH /api/attendance/<id>/`
- `DELETE /api/attendance/<id>/`

Custom attendance actions:
- `POST /api/attendance/bulk/`
- `GET /api/attendance/summary/`
- `GET /api/attendance/export/`

### User Role Update
- `PATCH /api/users/<id>/role/`

## Data Model Notes

### User
- custom `User` model extending `AbstractUser`
- includes `role` field with choices:
  - `admin`
  - `teacher_hr`
  - `member`

### Department
- `name` must be unique

### Member
- linked to a Django user via one-to-one relation
- has a unique `employee_id`
- belongs to a department

### Attendance
- each member can only have one attendance record per date
- status can be one of:
  - `present`
  - `absent`
  - `leave`

## Security Notes

This project follows a secure-by-default approach:
- environment variables are used for sensitive config
- no hardcoded secrets are committed
- Django password validation is enabled
- JWT authentication is used instead of session-based auth for API access
- role checks are enforced through custom permission classes
- all DB access is expected to use Django ORM parameterized queries

## Production Recommendations

Before moving this app to production:
- use a real secret manager or secure environment injection
- set `DEBUG=false`
- restrict `ALLOWED_HOSTS`
- use HTTPS only
- configure PostgreSQL credentials securely
- include CSRF and CORS controls if frontend access is expanded
- add rate limiting and audit logging
- enable database backups and monitoring

## Troubleshooting

### Django says settings are not configured
Ensure you run commands from the project root and the module loads properly:

```bash
python manage.py check
```

### PostgreSQL connection errors
Check:
- database exists
- username/password are correct
- host and port are valid
- PostgreSQL server is running
- firewall / local network rules allow access

### `psycopg` import errors
Install the adapter:

```bash
pip install psycopg[binary]
```

## License

This project is licensed under the terms of the MIT License. See the `LICENSE` file for details.

## Contributing

Pull requests are welcome. Please keep changes focused, well-tested, and aligned with the project’s security and API design standards.
