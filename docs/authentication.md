# Authentication Documentation

## User Authentication
The application supports two authentication methods:

### 1. Regular User Authentication
- Users can register and login using username/password
- Registration requires:
  - First name
  - Last name 
  - Email (must be unique)
  - Username (4-25 characters)
  - Password

### 2. Admin Authentication
- Admins authenticate via Google OAuth2
- Only emails listed in `ADMIN_EMAILS` env variable are allowed
- Admin authentication flow:
  1. Click "Sign in with Google" on login page
  2. Authenticate with Google
  3. Email is verified against allowed admin emails
  4. Admin session is created

## Implementation Details

### Regular Users
- Username/password stored in MongoDB
- Session-based authentication using Flask sessions
- Password validation on registration
- Email uniqueness check
- Username availability check

### Admin Users 
- Google OAuth2 authentication
- Admin emails configured in `.env` file
- Admin credentials stored in separate MongoDB collection
- Session contains:
  - google_id
  - name
  - email

## Access Tokens and Password Changes
- API requests carry a JWT in the `Authorization: Bearer` header; it expires after `JWT_EXPIRE_HOURS` (default 24).
- Changing or resetting a password stores `password_changed_at` on the user. Any token issued before that moment is rejected with `401`, so a stolen or forgotten session cannot outlive the password it was opened with.
- `PATCH /api/auth/change-password` returns a fresh `access_token` for the session that made the change, and `POST /api/auth/set-password` (reset) already returns one.
