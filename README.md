User Auth API
A FastAPI-based authentication API with JWT access tokens, rotating refresh tokens, Argon2 password hashing, and SQLAlchemy-backed persistence.

This project is a complete authentication backend. It supports user registration, login, token refresh (with rotation and revocation), and logout. Access tokens are short-lived JWTs; refresh tokens are opaque, stored hashed in the database, and rotated on each use.


Features
User Registration – Unique name and email enforcement with Argon2-hashed passwords
Login – Returns both an access token and a refresh token
JWT Access Tokens – Short-lived bearer tokens (default 30 minutes)
Refresh Token Rotation – Each refresh issues a brand-new refresh token and revokes the old one
Token Revocation / Logout – Refresh tokens are stored server-side and can be revoked
Protected Routes – GET /users/me guarded by OAuth2 bearer auth
Database Tables Auto-Created – Via FastAPI's lifespan hook on startup
Alembic Migrations – Schema versioning support
Full Pytest Suite – Covers registration, login, refresh rotation, logout, and auth failures


Tech Stack
Auth	JWT (PyJWT) + opaque rotating refresh tokens
Password Hashing	Argon2 via pwdlib
ORM	SQLAlchemy
Migrations	Alembic
Config	pydantic-settings (.env file)
Testing	Pytest + FastAPI TestClient



Installation
Clone the repository

bash
git clone https://github.com/ajide08/user-auth-api.git
cd user-auth-api
Create and activate a virtual environment

bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Configure environment variables

Create a .env file in the project root:

env
DATABASE_URL=sqlite:///./auth.db
SECRET_KEY=your-super-secret-key-change-me
Optional overrides (defaults shown):

env
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
Run the development server

bash
uvicorn app.main:app --reload
Database tables are created automatically on startup via the app's lifespan hook.

Explore the API docs

Open http://localhost:8000/docs for the interactive Swagger UI.

API Endpoints
All auth endpoints are prefixed with /auth; user endpoints with /users.

Method	Endpoint	Description	Auth Required
POST	/auth/register	Register a new user	No
POST	/auth/login	Log in, receive access + refresh tokens	No
POST	/auth/refresh	Exchange a refresh token for a new token pair	No (refresh token in body)
POST	/auth/logout	Revoke a refresh token	No (refresh token in body)
GET	/users/me	Get the current user's profile	Yes (Bearer access token)

Request / Response Schemas

UserInCreate (register request)

json
{ "name": "string", "email": "user@example.com", "password": "string" }
UserOutput (register / me response)

json
{ "id": 1, "name": "string", "email": "user@example.com" }


UserInLogin (login request)

json
{ "email": "user@example.com", "password": "string" }
TokenResponse (login / refresh response)

json
{
  "token_type": "bearer",
  "access_token": "eyJ...",
  "refresh_token": "<token_id>.<secret>",
  "user": null
}


RefreshTokenRequest (refresh / logout request)

json
{ "refresh_token": "<token_id>.<secret>" }
Example: Register
bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Ayomide", "email": "ayo@example.com", "password": "hello123"}'
Returns 201 Created with the user object (no password fields).


Example: Login
bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ayo@example.com", "password": "hello123"}'
Example: Access a Protected Route
bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer <access_token>"
Example: Refresh Tokens
bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<token_id>.<secret>"}'
The old refresh token is revoked and a new pair is returned (rotation).


Example: Logout
bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<token_id>.<secret>"}'
Returns {"message": "Logged out successfully"}.

Error Responses
