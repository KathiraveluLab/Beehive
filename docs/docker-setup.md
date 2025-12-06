
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
- To access admin, add `{"role": "admin"}` in the user's public metadata in Clerk Dashboard

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
- MongoDB: `localhost:27017` (containerized)


**Stop:** `Ctrl+C` or `docker compose down`

**Restart:** `docker compose up`

