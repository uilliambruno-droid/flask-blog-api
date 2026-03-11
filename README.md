# Flask Blog API

A portfolio-ready REST API built with Flask, JWT authentication, role-based authorization, SQLAlchemy ORM, and automated tests.

## Overview

This project simulates the backend of a blog platform and focuses on clean project structure, authentication, authorization, CRUD operations, and automated validation through unit and integration tests.

It was developed as a backend portfolio project to demonstrate practical skills in:

- Flask application architecture
- REST API design
- JWT authentication
- role-based access control
- SQLAlchemy models and database interaction
- automated testing with `pytest`

## Highlights

- JWT-based authentication flow with login endpoint
- Role-based authorization for `admin` and `normal` users
- CRUD coverage for users and posts
- Role creation with duplicate handling
- Password hashing with `Flask-Bcrypt`
- Validation for user creation using Marshmallow
- JSON error responses for HTTP exceptions
- Automated test suite with unit and integration coverage

## Tech Stack

- Python 3.14
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flask-Bcrypt
- Flask-Marshmallow
- Marshmallow-SQLAlchemy
- SQLite
- Pytest
- Poetry

## Project Structure

```text
flask-blog-api/
├── src/
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   ├── controllers/
│   │   ├── auth.py
│   │   ├── post.py
│   │   ├── role.py
│   │   └── user.py
│   ├── models/
│   │   ├── base.py
│   │   ├── post.py
│   │   ├── role.py
│   │   └── user.py
│   ├── views/
│   ├── utils.py
│   └── wsgi.py
├── migrations/
├── tests/
└── README.md
```

## Implemented Endpoints

### Auth

- `POST /auth/login` — authenticate a user and return a JWT token

### Users

- `GET /users/` — list users (`admin` only)
- `POST /users/` — create user (`admin` only)
- `GET /users/<user_id>` — retrieve user details (authenticated)
- `DELETE /users/<user_id>` — delete user (`admin` only)

### Roles

- `POST /roles/` — create a role (`admin` only)

### Posts

- `GET /posts/` — list posts (`normal` role)
- `POST /posts/` — create post (`normal` role)
- `GET /posts/<post_id>` — retrieve a post (`normal` role)
- `PATCH /posts/<post_id>` — update a post (`normal` role)
- `DELETE /posts/<post_id>` — delete a post (`normal` role)

### Docs / Error Handling

- `GET /docs` — returns generated OpenAPI data for documented routes
- JSON responses for `404` and other HTTP exceptions

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/uilliambruno-droid/flask-blog-api.git
cd flask-blog-api
```

### 2. Install dependencies

```bash
poetry install
```

### 3. Run the application

```bash
poetry run flask --app src.app:create_app --debug run
```

The API will be available at `http://127.0.0.1:5000`.

## Running Tests

```bash
poetry run pytest -q
```

Current validated suite status:

- `61 passed`

## Example Requests

### Login

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john-wick", "password": "test"}'
```

### Create a user as admin

```bash
curl -X POST http://127.0.0.1:5000/users/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "new-user", "password": "secret123", "role_id": 1}'
```

### Create a post as normal user

```bash
curl -X POST http://127.0.0.1:5000/posts/ \
  -H "Authorization: Bearer YOUR_NORMAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Post", "body": "Post content", "author_id": 2}'
```

## Why This Project Matters

This project is intended to showcase backend engineering fundamentals in a practical way. It demonstrates not only the implementation of API endpoints, but also concern for:

- authorization rules
- error handling
- testability
- maintainability
- realistic development workflow

## Possible Next Improvements

- add `pytest-cov` for measurable code coverage
- expand OpenAPI documentation for all endpoints
- add Docker support
- add `.env.example`
- add pagination and filtering for list endpoints
- add CI with GitHub Actions

## License

This project is available under the MIT License.
