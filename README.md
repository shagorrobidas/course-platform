# Course Platform - Django Backend API

<p>A comprehensive online course platform built with Django REST Framework, featuring user authentication, course management, progress tracking, and real-time notifications.</p>

## Features
- **🔐 Authentication System:** JWT-based authentication with email verification and OTP
- **👥 Role-Based Access:** Students, Teachers, and Admin roles with different permissions
- **📚 Course Management:** Create, update, and manage courses with modules and lessons
- **🎯 Progress Tracking:** Percentage-based progress tracking with completion status
- **💬 Real-time Notifications:** WebSocket support for live Q&A and updates
- **📧 Email System:** Welcome emails, enrollment confirmations, and notifications
- **🏆 Certificate Generation:** Automatic PDF certificates upon course completion
- **📊 Analytics & Reports:** Student progress reports and course analytics
- **🔍 Search & Filtering:** Advanced filtering for courses and content
- **📱 RESTful API:** Complete REST API with CRUD operations

## Tech Stack

- **Backend:** Django 4.2.7 + Django REST Framework 3.14.0
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Authentication:** JWT with Simple JWT
- **Real-time:** Django Channels + Redis
- **Task Queue:** Celery + Redis for background jobs
- **File Storage:** AWS S3 for media files
- **Email:** SMTP with TLS encryption

##  Prerequisites

- Python 3.11.6+
- PostgreSQL 13+
- Redis 6+
- AWS Account (for S3 storage)

## Quick Start
1. **Clone the repository**
    ```
    git clone https://github.com/yourusername/course-platform.git
    cd course-platform
    ```

2. **Create virtual environment**
    ```
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # or
    venv\Scripts\activate     # Windows

    ```

3. **Install dependencies**
    ```
    pip install -r requirements.txt
    ```

4. **Environment setup**
    ```
    cp .env.example .env
    # Edit .env with your configuration
    ```

5. **Database setup**
    ```
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    ```

6. **Run development server**
    ```
    python manage.py runserver
    ```

7. **Start Celery worker (new terminal)**
    ```
    celery -A course_platform worker --loglevel=info
    ```
8. **Start Redis (required for Celery)**
    ```
    redis-server
    ```

## Project Structure


    course_platform/
    ├── core/          # Main project
    │   ├── settings/
    │   │   ├── base.py          # Base settings
    │   │   ├── production.py    # Production config
    │   │   └── development.py   # Development config
    │   ├── urls.py              # URL routing
    │   └── asgi.py              # ASGI config
    ├── users/                   # Authentication app
    │   ├── models.py           # User model
    │   ├── serializers.py      # User serializers
    │   ├── views.py           # Auth views
    │   └── urls.py            # Auth endpoints
    ├── courses/                # Courses app
    │   ├── models.py          # Course models
    │   ├── serializers.py     # Course serializers
    │   ├── views.py          # Course views
    │   └── urls.py           # Course endpoints
    ├── notifications/         # WebSocket app
    │   ├── consumers.py      # WebSocket handlers
    │   └── routing.py        # WebSocket routes
    ├── core/                  # Core utilities
    │   ├── tasks.py          # Celery tasks
    │   └── utils.py          # Helper functions
    ├── static/               # Static files
    ├── templates/            # Email templates
    ├── build.sh             # Build script
    ├── render.yaml          # Render config
    ├── requirements.txt     # Dependencies
    └── runtime.txt          # Python version


## API Endpoints

### Base URL
```
https://127.0.0.1:800/api/v1/course/
```

### Authentication Endpoints

All auth endpoints are prefixed with: /api/v1/auth/

