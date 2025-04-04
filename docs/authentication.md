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