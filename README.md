# Job Application Tracker / Placement Portal

A Flask-based Job Application Tracker project where users can register, login, and manage their job applications.  
This project includes JWT authentication, SQLAlchemy ORM, Flask-Migrate, REST APIs, pagination, search/filter, API key protection, rate limiting, and a basic frontend.

---

## Features

- User registration and login
- Password hashing
- JWT authentication
- Protected job APIs
- Add job application
- View all job applications
- View single job application
- Update job application
- Delete job application
- Search jobs by company or role
- Filter jobs by status, job type, and location
- Pagination
- Dashboard summary API
- API key protected route
- Rate limiting
- Frontend pages connected with APIs
- SQLAlchemy ORM
- Flask-Migrate database migrations
- MySQL database

---

## Tech Stack

- Python
- Flask
- MySQL
- SQLAlchemy
- Flask-Migrate
- PyJWT
- Flask-Limiter
- HTML
- CSS
- JavaScript Fetch API
- Postman

---

## Project Structure

```text
job_tracker_project/
├── app.py
├── config.py
├── extensions.py
├── .env
├── requirements.txt
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── job.py
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── auth_utils.py
│   └── job_routes.py
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── jobs.html
│   ├── add_job.html
│   └── edit_job.html
└── static/
    └── style.css