
## Run with Docker

### 1. Clone Repository
```bash
git clone https://github.com/kathiravelulab/Beehive.git
cd Beehive
```

### 2. Configure Environment & Authentication

This project uses JWT-based authentication for the backend and local-storage tokens in the frontend.

**JWT Setup:**
- Set a strong `JWT_SECRET` in your `.env` (or Docker environment). This secret is used to sign and verify access tokens.
- Optionally adjust token lifetime with `JWT_EXPIRE_HOURS` (default 24).

**Google OAuth:**
- Create OAuth credentials in Google Cloud Console
- Download `client_secret.json` to project root
- Add redirect URI: `http://localhost:5000/admin/login/callback`

**Root `.env`:**
```env
MONGODB_URI=mongodb://mongo:27017/beehive
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
REDIRECT_URI=http://localhost:5000/admin/login/callback
ADMIN_EMAILS=admin1@example.com,admin2@example.com
JWT_SECRET=your_jwt_secret_here
JWT_EXPIRE_HOURS=24
FLASK_SECRET_KEY=your_custom_flask_secret
# CORS Configuration (Optional - comma-separated list of allowed origins)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

**Frontend `.env`:**
```env
# No Clerk publishable key required for JWT-based auth. Frontend stores tokens in localStorage.
```

### 3. Run Docker

**Start:**
```bash
docker compose up --build
```

**Access:**
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:5173`
- Admin Dashboard: `http://localhost:5173/admin` (requires admin role setup - see Clerk Setup above)
- MongoDB: `localhost:27017` (containerized)


**Stop:** `Ctrl+C` or `docker compose down`

**Restart:** `docker compose up`
