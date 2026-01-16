# Django Auth Service with OTP, JWT, and Password Flows

This project is an **authentication service** built with Django and Django REST Framework (DRF) that supports:

- Email/password registration & login
- Email-based OTP login (password + OTP)
- Forgot password / password reset via OTP
- JWT authentication (`access` + `refresh`)
- Audit logging
- Rate-limiting and OTP storage in Redis
- Asynchronous email sending via Celery
- Complete OpenAPI documentation via **drf-spectacular**
- Dockerized development environment

---

## Table of Contents

- [Django Auth Service with OTP, JWT, and Password Flows](#django-auth-service-with-otp-jwt-and-password-flows)
  - [Table of Contents](#table-of-contents)
  - [Tech Stack](#tech-stack)
  - [Requirements](#requirements)
  - [Setup (Local)](#setup-local)
  - [Setup (Docker)](#setup-docker)
  - [Running the Project](#running-the-project)

---

## Tech Stack

- Python 3.11+
- Django 5.x
- Django REST Framework
- drf-spectacular
- Redis (OTP & rate limiting)
- Celery (async email sending & audit logging)
- djangorestframework-simplejwt
- Docker + docker-compose (optional)

---

## Requirements

- Python 3.11+
- Redis server (local or Docker)
- Node.js (optional, for frontend demo)
- Docker & docker-compose (optional)

---

## Setup (Local)

1. **Clone the repository**

```bash
git clone https://github.com/Clemcy9/drf-otp-auth.git
cd drf-otp-auth
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Set environment variables**

Create a .env file in the project root:

```env
- SECRET_KEY=your-django-secret-key
- DEBUG=True
- ALLOWED_HOSTS=localhost,127.0.0.1
- REDIS_HOST=127.0.0.1
- REDIS_PORT=6379
- CELERY_BROKER_URL=redis://127.0.0.1:6379/0
```

3. **Run migrations**

```bash
python manage.py migrate

```

4. **Create a superuser**

```bash
python manage.py createsuperuser
```

## Setup (Docker)

1. **Build and start services**

```bash
docker-compose up --build
```

This starts:

Django API on http://localhost:8000

Redis server

Celery worker for async tasks

2. **Run migrations in Docker**

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Running the Project

1. **Start Django server locally**

```bash
python manage.py runserver
```

Start Celery worker

celery -A config.celery_app worker -l info

Start Celery beat (optional, for scheduled tasks)

celery -A config.celery_app beat -l info

API Documentation

Swagger UI: http://localhost:8000/api/docs/

Redoc UI: http://localhost:8000/api/redoc/

All endpoints show request bodies, examples, and JWT auth requirements.

Auth Flows

1. Password-based authentication
   Endpoint Method Body
   /api/v1/auth/register POST {"email": "user@example.com", "password": "secret"}
   /api/v1/auth/login POST {"email": "user@example.com", "password": "secret"} → Returns OTP sent to email
   /api/v1/auth/login/otp-verify POST {"email": "user@example.com", "otp": "123456"} → Returns JWT tokens
   /api/v1/auth/forgot-password POST {"email": "user@example.com"} → Sends OTP to email
   /api/v1/auth/password-reset POST {"email": "...", "otp": "123456", "password": "newpass"}
2. OTP-based authentication
   Endpoint Method Body
   /api/v1/auth/otp/request POST {"email": "user@example.com"} → Sends OTP to email
   /api/v1/auth/otp/verify POST {"email": "user@example.com", "otp": "123456"} → Returns JWT tokens
3. Protected endpoints

/api/v1/auth/me → GET current user info (JWT required)

/api/v1/auth/profile → PUT update profile info (JWT required)

/api/v1/audit/logs → GET audit logs (JWT required)

Environment Variables
Variable Purpose Example
SECRET_KEY Django secret key super-secret-key
DEBUG Debug mode True
ALLOWED_HOSTS Hosts allowed localhost,127.0.0.1
REDIS_HOST Redis hostname 127.0.0.1
REDIS_PORT Redis port 6379
CELERY_BROKER_URL Celery broker URL redis://127.0.0.1:6379/0
Notes

OTP storage: Redis with TTL (5 min)

Rate limiting: Redis counters per email & per IP

Audit logging: Asynchronous via Celery

Email sending: Celery prints to console by default
