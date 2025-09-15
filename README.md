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

3. **Create virtual environment**
    ```
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # or
    venv\Scripts\activate     # Windows

    ```

4. **Install dependencies**
    ```
    pip install -r requirements.txt
    ```

5. **Environment setup**
    ```
    cp .env.example .env
    # Edit .env with your configuration
    ```

6. **Database setup**
    ```
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
   ```

7. **Run development server**
    ```
    python manage.py runserver
    ```

8. Start Celery worker (new terminal)
    ```
    celery -A course_platform worker --loglevel=info
    ```
9. Start Redis (required for Celery)
    ```
    redis-server
    ```
