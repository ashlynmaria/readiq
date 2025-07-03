# ReadIQ API

A simple **FastAPI + PostgreSQL** backend for user authentication, role-based access, and user management.

---

## 🚀 Features

- JWT authentication
- Register and login
- Password hashing
- Protected routes
- Admin-only user listing
- User activation/deactivation/reactivation
- Alembic migrations

---

## 📦 Setup

1. **Create and activate your virtual environment:**

```bash
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up your database:**

- PostgreSQL with a database called `readiq`  
  - user: `readiq`  
  - password: `readiq`

4. **Run Alembic migrations:**

```bash
alembic upgrade head
```

5. **Start the server:**

```bash
uvicorn main:app --reload
```

---

## 🧪 Test API with curl

### Register a new user

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register"   -H "Content-Type: application/json"   -d '{"username":"newuser","password":"newpassword"}'
```

### Login

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login"   -H "Content-Type: application/json"   -d '{"username":"newuser","password":"newpassword"}'
```

Copy the returned token.

---

## 🔐 Protected routes

### Get current user profile

```bash
curl -X GET "http://127.0.0.1:8000/api/protected/me"   -H "Authorization: Bearer <token>"
```

### Change password

```bash
curl -X POST "http://127.0.0.1:8000/api/protected/change-password"   -H "Authorization: Bearer <token>"   -H "Content-Type: application/json"   -d '{"new_password": "supersecure123"}'
```

### Update profile

```bash
curl -X POST "http://127.0.0.1:8000/api/protected/update-profile"   -H "Authorization: Bearer <token>"   -H "Content-Type: application/json"   -d '{"username": "updatedname"}'
```

### Delete account

```bash
curl -X DELETE "http://127.0.0.1:8000/api/protected/delete-account"   -H "Authorization: Bearer <token>"
```

---

## 🛠 Admin only

### Login as admin

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login"   -H "Content-Type: application/json"   -d '{"username":"adminuser","password":"adminpass"}'
```

### List all users

```bash
curl -X GET "http://127.0.0.1:8000/api/protected/all-users"   -H "Authorization: Bearer <admin_token>"
```

### Deactivate a user

```bash
curl -X POST "http://127.0.0.1:8000/api/protected/deactivate-user/1"   -H "Authorization: Bearer <admin_token>"
```

### Reactivate a user

```bash
curl -X POST "http://127.0.0.1:8000/api/protected/reactivate-user/1"   -H "Authorization: Bearer <admin_token>"
```

---

## 🗂 Tech stack

- FastAPI  
- SQLAlchemy  
- Alembic  
- PostgreSQL  
- Pydantic  
- JWT (via `python-jose`)  
- bcrypt
