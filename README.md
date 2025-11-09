# Role-Based Access Control (RBAC) API with React Frontend

A scalable REST API with JWT authentication and role-based access control, featuring a React frontend for testing and demonstration.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Frontend Usage](#frontend-usage)
- [Default Admin Accounts](#default-admin-accounts)
- [Security Features](#security-features)

## Features

### Backend
- ✅ User registration and login with JWT authentication
- ✅ Password hashing using bcrypt
- ✅ Role-based access control (User vs Admin)
- ✅ CRUD operations for Tasks and Notes
- ✅ API versioning (v1)
- ✅ Comprehensive error handling and validation
- ✅ MongoDB integration with Motor (async driver)
- ✅ Automatic admin account seeding
- ✅ Input sanitization and validation using Pydantic

### Frontend
- ✅ User authentication (Login/Register)
- ✅ Protected dashboard with role-based views
- ✅ Task management (CRUD operations)
- ✅ Note management (CRUD operations)
- ✅ User management (Admin only)
- ✅ Error and success message handling
- ✅ Responsive design with modern UI
- ✅ JWT token management

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Bcrypt** - Password hashing

### Frontend
- **React 19** - UI library
- **React Router** - Navigation
- **Axios** - HTTP client
- **CSS** - Styling (no framework)

## Project Structure

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── .env                   # Environment variables
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Global styles
│   │   └── components/
│   │       ├── Login.js      # Login page
│   │       ├── Register.js   # Registration page
│   │       ├── Dashboard.js  # Main dashboard
│   │       ├── Tasks.js      # Task management
│   │       ├── Notes.js      # Note management
│   │       └── Users.js      # User management (Admin)
│   ├── package.json
│   └── .env
└── README.md
```

## Installation

### Backend Setup

1. Install dependencies:
```bash
cd /app/backend
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="Assignment"
CORS_ORIGINS="*"
JWT_SECRET_KEY="your-secret-key-change-in-production"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_MINUTES=1440
```

3. Start the server:
```bash
sudo supervisorctl restart backend
```

The API will be available at `http://localhost:8001`

### Frontend Setup

1. Install dependencies:
```bash
cd /app/frontend
yarn install
```

2. Configure environment variables in `.env`:
```env
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

3. Start the development server:
```bash
yarn start
```

The app will be available at `http://localhost:3000`

## API Documentation

### Base URL
```
http://localhost:8001/api/v1
```

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}

Response (201):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "john@example.com",
    "name": "John Doe",
    "role": "user",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "email": "john@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2025-01-01T00:00:00Z"
}
```

### Task Endpoints

#### Create Task
```http
POST /api/v1/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "status": "todo",
  "priority": "high"
}

Response (201):
{
  "id": "uuid",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "status": "todo",
  "priority": "high",
  "user_id": "uuid",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### Get All Tasks
```http
GET /api/v1/tasks
Authorization: Bearer <token>

Response (200):
[
  {
    "id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "status": "in_progress",
    "priority": "medium",
    "user_id": "uuid",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

**Note:** Users can only see their own tasks. Admins can see all tasks.

#### Get Single Task
```http
GET /api/v1/tasks/{task_id}
Authorization: Bearer <token>

Response (200): Task object
```

#### Update Task
```http
PUT /api/v1/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated title",
  "status": "completed"
}

Response (200): Updated task object
```

#### Delete Task
```http
DELETE /api/v1/tasks/{task_id}
Authorization: Bearer <token>

Response (204): No content
```

### Note Endpoints

#### Create Note
```http
POST /api/v1/notes
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Meeting Notes",
  "content": "Discussed project timeline and deliverables",
  "tags": ["meeting", "project", "important"]
}

Response (201):
{
  "id": "uuid",
  "title": "Meeting Notes",
  "content": "Discussed project timeline and deliverables",
  "tags": ["meeting", "project", "important"],
  "user_id": "uuid",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### Get All Notes
```http
GET /api/v1/notes
Authorization: Bearer <token>

Response (200): Array of note objects
```

**Note:** Users can only see their own notes. Admins can see all notes.

#### Get Single Note
```http
GET /api/v1/notes/{note_id}
Authorization: Bearer <token>

Response (200): Note object
```

#### Update Note
```http
PUT /api/v1/notes/{note_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated title",
  "content": "Updated content",
  "tags": ["updated", "modified"]
}

Response (200): Updated note object
```

#### Delete Note
```http
DELETE /api/v1/notes/{note_id}
Authorization: Bearer <token>

Response (204): No content
```

### User Management Endpoints (Admin Only)

#### Get All Users
```http
GET /api/v1/users
Authorization: Bearer <admin-token>

Response (200):
[
  {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "role": "user",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### Delete User
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <admin-token>

Response (204): No content
```

### Health Check
```http
GET /api/v1/health

Response (200):
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Frontend Usage

### User Flow

1. **Registration/Login**
   - Navigate to the login page
   - Register a new account or log in with existing credentials
   - Upon successful authentication, you'll be redirected to the dashboard

2. **Dashboard**
   - View your profile information (name, role)
   - Access different sections via tabs (Tasks, Notes, Users*)
   - *Users tab is only visible to admin accounts

3. **Task Management**
   - Create new tasks with title, description, status, and priority
   - View all your tasks (admins see all tasks)
   - Edit existing tasks
   - Delete tasks
   - Tasks are color-coded by priority and status

4. **Note Management**
   - Create new notes with title, content, and tags
   - View all your notes (admins see all notes)
   - Edit existing notes
   - Delete notes
   - Tags help organize and categorize notes

5. **User Management (Admin Only)**
   - View all registered users
   - See user details (name, email, role, creation date)
   - Delete users

## Default Admin Accounts

Three admin accounts are automatically created on first startup:

1. **Admin: Aanushka**
   - Email: `aanushka@admin.com`
   - Password: `Admin@123`

2. **Admin One**
   - Email: `admin1@admin.com`
   - Password: `Admin@123`

3. **Admin Two**
   - Email: `admin2@admin.com`
   - Password: `Admin@123`

## Security Features

### Backend Security

1. **Password Hashing**
   - All passwords are hashed using bcrypt before storage
   - No plain-text passwords are stored in the database

2. **JWT Authentication**
   - Secure token-based authentication
   - Tokens include user ID, email, and role
   - Configurable expiration time (default: 24 hours)

3. **Role-Based Access Control**
   - Two roles: `user` and `admin`
   - Users can only access their own resources
   - Admins can access all resources and manage users

4. **Input Validation**
   - All inputs validated using Pydantic models
   - Email validation for user registration
   - Required field validation
   - Type checking and coercion

5. **CORS Configuration**
   - Configurable allowed origins
   - Credentials support for secure cookie handling

6. **Error Handling**
   - Comprehensive error messages
   - Proper HTTP status codes
   - Detailed validation errors

### Frontend Security

1. **Token Management**
   - JWT tokens stored in localStorage
   - Automatic token injection in API requests
   - Token validation on protected routes

2. **Protected Routes**
   - Authentication required for dashboard access
   - Automatic redirect to login for unauthenticated users

3. **Role-Based UI**
   - Admin-only features hidden from regular users
   - Dynamic component rendering based on role

## Database Schema

### Users Collection
```javascript
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "password": "$2b$12$hashed_password",
  "role": "user" | "admin",
  "created_at": "ISO 8601 timestamp"
}
```

### Tasks Collection
```javascript
{
  "id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "status": "todo" | "in_progress" | "completed",
  "priority": "low" | "medium" | "high",
  "user_id": "uuid",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

### Notes Collection
```javascript
{
  "id": "uuid",
  "title": "Note title",
  "content": "Note content",
  "tags": ["tag1", "tag2"],
  "user_id": "uuid",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

## API Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid email or password"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Testing with cURL

### Register a new user
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Create a task (with token)
```bash
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "My First Task",
    "description": "This is a test task",
    "status": "todo",
    "priority": "high"
  }'
```

### Get all tasks
```bash
curl -X GET http://localhost:8001/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

## Scalability Features

1. **Modular Architecture**
   - Clear separation of concerns
   - Easy to add new endpoints and features
   - Reusable authentication and authorization logic

2. **Async Operations**
   - Motor async driver for MongoDB
   - Non-blocking database operations
   - Better performance under load

3. **API Versioning**
   - All endpoints prefixed with `/api/v1`
   - Easy to add new versions without breaking existing clients

4. **Database Indexing**
   - Recommended indexes for production:
     ```javascript
     db.users.createIndex({ "email": 1 }, { unique: true })
     db.tasks.createIndex({ "user_id": 1 })
     db.notes.createIndex({ "user_id": 1 })
     ```

## Future Enhancements

- [ ] Email verification for new users
- [ ] Password reset functionality
- [ ] Refresh token mechanism
- [ ] Rate limiting
- [ ] API request logging
- [ ] Task sharing between users
- [ ] Note collaboration features
- [ ] Search and filtering capabilities
- [ ] Pagination for large datasets
- [ ] Export data functionality

## License

MIT License

## Support

For issues or questions, please create an issue in the repository or contact the development team.