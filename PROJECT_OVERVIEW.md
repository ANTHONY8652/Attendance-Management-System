# Attendance Management System

## Project Summary

This project is an attendance management platform built with Django REST Framework. It manages users, departments, members, and attendance records through a REST API. The system is designed for role-based access, so administrators, HR/teachers, and regular members have different permissions.

## Technology Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT using `djangorestframework-simplejwt`
- **Filtering:** `django-filter`
- **Frontend:** React and Vite
- **Database driver:** `psycopg`

## Core Models

### User

The custom user model extends Django's `AbstractUser` and adds a role:

- `admin`
- `teacher_hr`
- `member`

### Department

Stores department names and timestamps.

### Member

Connects a user to an employee ID and department.

### Attendance

Stores a member's attendance status for a specific date:

- `present`
- `absent`
- `leave`

Each member can have only one attendance record per date.

## Authentication and Security

- Users authenticate through JWT login endpoints.
- Access tokens are short-lived.
- Refresh tokens rotate when used.
- Rotated refresh tokens are blacklisted.
- The Django secret key is loaded from environment configuration.
- Local `.env` files are excluded from Git.
- Role-based permissions restrict administrative and staff actions.
- Members can only access their own member and attendance records.

## Main API Endpoints

```text
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/refresh/
PATCH  /api/users/<id>/role/

GET    /api/departments/
POST   /api/departments/

GET    /api/members/
POST   /api/members/

GET    /api/attendance/
POST   /api/attendance/
POST   /api/attendance/bulk/
GET    /api/attendance/summary/
GET    /api/attendance/export/
```

## Important Behaviors

- Staff can create and update attendance records.
- Bulk attendance marking uses an atomic member/date workflow.
- Future attendance dates are rejected by validation.
- Attendance can be filtered by member, status, date range, and department.
- Attendance summaries provide totals for present, absent, and leave statuses.
- Attendance can be exported as CSV.
- Duplicate attendance records for the same member and date are rejected.

## Frontend

The React frontend provides:

- JWT login
- Overview dashboard
- Attendance record search
- Attendance creation form
- People and department views
- Responsive sidebar navigation
- Responsive desktop and mobile layouts

The frontend reads the API URL from `VITE_API_URL`, defaulting to:

```text
http://localhost:8000/api
```

## Testing

The Django test suite covers:

- Registration and JWT login
- Admin role updates
- Role-based permission restrictions
- Department permissions
- Member visibility isolation
- Attendance creation and filtering
- Duplicate attendance prevention
- Bulk attendance marking
- Attendance summaries
- Future-date validation

Run the backend checks with:

```bash
python manage.py check
python manage.py test
```

## Interview Explanation

> This is a Django REST Framework attendance management system backed by PostgreSQL. It uses a custom user model with role-based permissions and JWT authentication. Refresh tokens rotate and are blacklisted for better session security. The main domain models are users, departments, members, and attendance records. The API supports normal and bulk attendance marking, filtering, summaries, and CSV export. A React/Vite frontend consumes the API and provides dashboard, attendance, and people management screens.
