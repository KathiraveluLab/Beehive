
## Run with Docker

### 1. Clone Repository
```bash
git clone https://github.com/kathiravelulab/Beehive.git
cd Beehive
```

### 2. Configure Environment & Authentication

**Clerk Setup:**
- Sign up at [clerk.dev](https://clerk.dev) and create an application
- Get your Publishable and Secret Keys
- Navigate to **Configure** → **Sessions** → **Claims** and add:
```json
{
    "role": "{{user.public_metadata.role || 'user'}}"
}
```

**Grant Admin Access for Local Development:**

**Prerequisite:** Make sure the session claim is configured in Clerk Dashboard (Configure → Sessions → Claims) with `{"role": "{{user.public_metadata.role || 'user'}}"}` as mentioned above.

For detailed step-by-step instructions on how to grant admin access, see [Admin Access Guide](common/admin-access.md).

**Note:** This admin access is for local development only and uses your local Docker MongoDB instance, separate from production.

**Google OAuth:**
- Create OAuth credentials in Google Cloud Console
- Download `client_secret.json` to project root
- Add redirect URI: `http://localhost:5000/admin/login/callback`

**Root `.env`:**
```env
MONGODB_CONNECTION_STRING=mongodb://mongo:27017/beehive
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
REDIRECT_URI=http://localhost:5000/admin/login/callback
ADMIN_EMAILS=admin1@example.com,admin2@example.com
CLERK_SECRET_KEY=your-clerk-secret-key
FLASK_SECRET_KEY=your_custom_flask_secret
# CORS Configuration (Optional - comma-separated list of allowed origins)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

**`frontend/.env`:**
```env
VITE_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
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
