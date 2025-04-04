# API Documentation

## User Routes

### Authentication
- `GET /` - Home page
- `GET /login` - Login page
- `POST /login` - Login user
- `GET /register` - Registration page
- `POST /register` - Register new user
- `GET /logout` - Logout user

### User Profile
- `GET /profile` - User profile page
- `POST /upload` - Upload new image
- `POST /edit/<image_id>` - Edit image details
- `GET /delete/<image_id>` - Delete image

## Admin Routes
- `GET /signingoogle` - Google sign in page
- `GET /admin/login` - Initiate OAuth flow
- `GET /admin/login/callback` - OAuth callback handler
- `GET /admin` - Admin dashboard
- `GET /admin/logout` - Admin logout
- `GET /admin/users` - View all users
- `GET /admin/users/<username>` - View specific user's images

## Protected Routes
All routes except home, login and register require authentication.
Admin routes require Google OAuth authentication.