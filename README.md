# 🛡️ Role-Based Access Control (RBAC) API with React Frontend

A scalable **FastAPI + MongoDB (Motor)** backend with JWT authentication and role-based access control, paired with a modern **React frontend** for testing and demonstration.

---

## 🗂️ Project Structure

```
rbac-app/
├── backend/
│   ├── .env
│   ├── requirements.txt
│   ├── server.py
│   └── ...
├── frontend/
│   ├── .env
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── ...
│   └── ...
├── postman_collection.json
└── README.md
```

---

## ⚙️ Features

### 🔧 Backend
- JWT Authentication (Login/Register)
- Password hashing (bcrypt)
- Role-Based Access Control (`user` / `admin`)
- CRUD for Tasks and Notes
- Admin-only user management
- Async MongoDB with Motor
- Auto-admin seeding
- API versioning (`/api/v1`)
- Pydantic validation & error handling

### 💻 Frontend
- React 19 + React Router
- Login/Register/Dashboard UI
- Task & Note Management
- Admin User Management
- JWT Token handling (localStorage)
- Protected routes based on roles
- Responsive modern UI

---

## 🧱 Tech Stack

| Component | Technology |
|-----------|-------------|
| Backend | FastAPI, Motor, MongoDB |
| Auth | JWT |
| Passwords | Bcrypt |
| Frontend | React 19 |
| HTTP | Axios |
| Validation | Pydantic |
| Deployment | Supervisor / Uvicorn |

---

## 🧩 MongoDB Setup (Compass / CLI)

**Database:** `Assignment`  
**Collections:**
- `users`
- `admins`
- `tasks`
- `notes`

### 🔌 Connect via MongoDB Compass

1. Open **MongoDB Compass**
2. Click **"New Connection"**
3. Use the following connection string:
   ```
   mongodb://localhost:27017
   ```
4. Once connected, select the database:
   ```
   Assignment
   ```
5. You'll see four collections:
   - `users`
   - `admins`
   - `tasks`
   - `notes`

### 🧭 Example Documents

#### Collection: `users`
```json
{
  "_id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "password": "$2b$12$hashedpassword",
  "role": "user",
  "created_at": "2025-11-10T12:00:00Z"
}
```

#### Collection: `admins`
```json
{
  "_id": "uuid",
  "name": "Aanushka",
  "email": "aanushka@admin.com",
  "password": "$2b$12$hashedpassword",
  "role": "admin",
  "created_at": "2025-11-10T12:00:00Z"
}
```

#### Collection: `tasks`
```json
{
  "_id": "uuid",
  "title": "Complete project docs",
  "description": "Finalize the README and Postman collection",
  "status": "in_progress",
  "priority": "high",
  "user_id": "uuid",
  "created_at": "2025-11-10T12:00:00Z",
  "updated_at": "2025-11-10T12:00:00Z"
}
```

#### Collection: `notes`
```json
{
  "_id": "uuid",
  "title": "Meeting Notes",
  "content": "Discussed task assignments and progress",
  "tags": ["meeting", "project"],
  "user_id": "uuid",
  "created_at": "2025-11-10T12:00:00Z",
  "updated_at": "2025-11-10T12:00:00Z"
}
```

---

## 🔐 Default Admin Accounts (Testing)

| Name | Email | Password | Role |
|------|-------|----------|------|
| Aanushka | aanushka@admin.com | Admin@123 | admin |
| Admin One | admin1@admin.com | Admin@123 | admin |
| Admin Two | admin2@admin.com | Admin@123 | admin |

✅ You can log in with these accounts from the **React frontend** or directly via **Postman**.

---

## 🧮 Backend Configuration

**File:** `./backend/.env`

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="Assignment"
CORS_ORIGINS="http://localhost:3000"
JWT_SECRET_KEY="supersecretlocalkey"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_MINUTES=1440
```

### 📦 Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### ▶️ Run the server

```bash
uvicorn server:app --reload --port 8000
```

Backend will be available at:
👉 `http://localhost:8000/api/v1`

---

## 🌐 Frontend Configuration

**File:** `./frontend/.env`

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

### 📦 Install & Start

```bash
cd frontend
npm install
npm start
```

Frontend will be available at:
👉 `http://localhost:3000`

---

## 🧾 API Overview

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/register` | POST | ❌ | Register new user |
| `/api/v1/auth/login` | POST | ❌ | Login and get JWT |
| `/api/v1/auth/me` | GET | ✅ | Get current user |
| `/api/v1/tasks` | GET/POST | ✅ | Manage user tasks |
| `/api/v1/tasks/{id}` | PUT/DELETE | ✅ | Update/Delete task |
| `/api/v1/notes` | GET/POST | ✅ | Manage notes |
| `/api/v1/notes/{id}` | PUT/DELETE | ✅ | Update/Delete note |
| `/api/v1/users` | GET | ✅ (admin) | List all users |
| `/api/v1/users/{id}` | DELETE | ✅ (admin) | Delete user |
| `/api/v1/health` | GET | ❌ | Health check |

---

## 🧰 Quick cURL Tests

**Login (Admin):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"aanushka@admin.com","password":"Admin@123"}'
```

**Create Task:**

```bash
TOKEN="your_jwt_here"
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Write Docs","description":"Finish the README","status":"todo","priority":"high"}'
```

**Get All Tasks:**

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/tasks
```

**Admin - Get All Users:**

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users
```

---

## 🧠 MongoDB Index Recommendations

Run in Compass or mongo shell:

```javascript
use Assignment
db.users.createIndex({ "email": 1 }, { unique: true })
db.tasks.createIndex({ "user_id": 1 })
db.notes.createIndex({ "user_id": 1 })
db.admins.createIndex({ "email": 1 }, { unique: true })
```

---

### Backend Deployment
- Use Uvicorn with supervisor for production
- Set proper CORS origins for your domain
- Use environment variables for secrets
- Consider using MongoDB Compass for  database

### Frontend Deployment
- Build with `npm run build`

---


**Happy Coding! 🎉**
