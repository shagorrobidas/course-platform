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


## 🗂️ Project Structure

```
course_platform/
├── core/
│   ├── settings/
│   │   ├── base.py
│   │   ├── production.py
│   │   └── development.py
│   ├── urls.py
│   └── asgi.py
├── users/              # Authentication & profiles
├── courses/            # Course, module, lesson logic
├── notifications/      # WebSocket + notifications
├── static/
├── templates/
├── build.sh
├── render.yaml
├── requirements.txt
└── runtime.txt
```

---

## 🔗 API Overview
#### Base URL
```
https://127.0.0.1:800/api/v1/course/
```

### Authentication

All auth endpoints are prefixed with: /api/v1/auth/

| Method | Endpoint                | Description                       | Auth         |
|--------|------------------------ |-----------------------------------|--------------|
| POST   | /auth/register/         | Register new user                 | No           |
| POST   | /auth/login/            | User login                        | No           |
| POST   | /auth/logout/           | Logout user                       | JWT          |
| POST   | /auth/request-otp/      | Request OTP for verification      | No           |
| POST   | /auth/verify-otp/       | Verify OTP                        | No           |
| POST   | /auth/change-password/  | Change password                   | JWT          |
| POST   | /auth/reset-password/   | Password reset                    | No           |
| GET    | /auth/profile/          | Get user profile                  | JWT          |

---

### 📁 Category Endpoints

| Method | Endpoint                             | Description                | Auth       | Permissions   |
|--------|--------------------------------------|----------------------------|------------|--------------|
| GET    | /categories/                         | List all categories        | Optional   | None         |
| GET    | /category/detail/<int:pk>/           | Get category details       | Optional   | None         |
| POST   | /category/create/                    | Create new category        | JWT        | Admin/Teacher|
| PUT    | /category/<int:pk>/update/           | Update category            | JWT        | Admin/Teacher|
| DELETE | /category/<int:pk>/delete/           | Delete category            | JWT        | Admin Only   |

---

### 🎓 Course Endpoints

| Method | Endpoint                             | Description                | Auth       | Permissions   |
|--------|--------------------------------------|----------------------------|------------|--------------|
| GET    | /                                   | List all courses           | Optional   | None         |
| POST   | /create/                            | Create new course          | JWT        | Teacher/Admin|
| GET    | /detail/<int:pk>/                   | Get course details         | Optional   | None         |
| PUT    | /update/<int:pk>/                   | Update course              | JWT        | Teacher/Admin|
| DELETE | /delete/<int:pk>/                   | Delete course              | JWT        | Admin Only   |
| GET    | /analytics/<int:course_id>/         | Course analytics           | JWT        | Teacher/Admin|

---

### 📝 Enrollment Endpoints

| Method | Endpoint                             | Description                | Auth       | Permissions   |
|--------|--------------------------------------|----------------------------|------------|--------------|
| POST   | /enroll/<int:course_id>/             | Enroll in course           | JWT        | Student      |
| GET    | /enrollments/                        | Get user enrollments       | JWT        | Student      |

---

### 📦 Module Endpoints

| Method | Endpoint                                  | Description             | Auth      | Permissions     |
|--------|-------------------------------------------|-------------------------|-----------|-----------------|
| GET    | /modules/<int:course_id>/                 | List course modules     | JWT       | Enrolled Student|
| POST   | /modules/create/<int:course_id>/          | Create module           | JWT       | Teacher/Admin   |
| PUT    | /modules/update/<int:pk>/                 | Update module           | JWT       | Teacher/Admin   |
| DELETE | /modules/delete/<int:pk>/                 | Delete module           | JWT       | Admin Only      |

---

### 📚 Lesson Endpoints

| Method | Endpoint                                  | Description             | Auth      | Permissions     |
|--------|-------------------------------------------|-------------------------|-----------|-----------------|
| GET    | /lessons/<int:pk>/                        | Get lesson details      | JWT       | Enrolled Student|
| POST   | /lessons/create/<int:module_id>/          | Create lesson           | JWT       | Teacher/Admin   |
| PUT    | /lessons/update/<int:pk>/                 | Update lesson           | JWT       | Teacher/Admin   |
| DELETE | /lessons/delete/<int:pk>/                 | Delete lesson           | JWT       | Admin Only      |

---

### 📈 Progress Tracking

| Method | Endpoint                                      | Description             | Auth      | Permissions  |
|--------|-----------------------------------------------|-------------------------|-----------|-------------|
| GET    | /progress/                                   | List user progress      | JWT       | Student     |
| POST   | /progress/create/                            | Create progress record  | JWT       | Student     |
| PUT    | /progress/update/<int:pk>/                   | Update progress         | JWT       | Student     |
| POST   | /progress/bulk-update/                       | Bulk update progress    | JWT       | Student     |
| GET    | /progress/detail/<int:pk>/                   | Get progress details    | JWT       | Student     |
| GET    | /progress/stats/                             | Progress statistics     | JWT       | Student     |
| GET    | /progress-report/<int:course_id>/            | Course progress report  | JWT       | Student     |
| PUT    | /progress/<int:pk>/                          | Update lesson progress  | JWT       | Student     |

---

### 🔔 WebSocket Endpoints

Real-time notifications and Q&A via WebSocket:

| Endpoint                                   | Description                 | Auth      |
|---------------------------------------------|-----------------------------|-----------|
| ws://your-domain/ws/notifications/          | Real-time notifications     | JWT       |

---

## 🎯 Environment Variables

Copy `.env.example` to `.env` and configure:

- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL`
- `REDIS_URL`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`
- Others as needed for your setup

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 🤝 Contributing

Pull requests and issues are **welcome**! Your feedback and ideas help us improve.

---

## 📝 License

[MIT License](LICENSE)

---

## 🙋 Contact

- Author: [@shagorrobidas](https://github.com/shagorrobidas)
- Repo: [shagorrobidas/course-platform](https://github.com/shagorrobidas/course-platform)

---

<p align="center">
  <b>Built with ❤️ using Django REST Framework, Channels, Celery, Redis</b>
</p>


