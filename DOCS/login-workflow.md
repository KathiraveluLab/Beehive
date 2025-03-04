# Beehive Login Workflow Documentation

This document outlines the authentication flows for both regular users and administrators in the Beehive application.

## Authentication Methods Overview

The application supports two authentication methods:
- Traditional username/password login
- Google Sign-In (OAuth 2.0)

## Regular User Authentication Flow

### New User Registration (Traditional)
1. User navigates to `/register`
2. User completes the registration form with:
   - First name
   - Last name
   - Email
   - Username
   - Password
3. System validates:
   - Username follows pattern rules
   - Email is valid and not already in use
   - Username is not already taken
   - Passwords match 
4. User account is created in the database
5. User is redirected to the login page

### New User via Google Sign-In
1. User clicks "Sign in with Google" button
2. User authorizes the application in Google's consent screen
3. If the email is not associated with an existing account:
   - User is redirected to `/register/google`
   - User completes a simplified registration form (username, first/last name)
   - System creates an account linked to their Google ID
4. User is redirected to their profile page

### Existing User Login (Traditional)
1. User navigates to `/login`
2. User enters username and password
3. System validates credentials
4. Upon successful validation:
   - User session is established
   - User is redirected to their profile page

### Existing User via Google Sign-In
1. User clicks "Sign in with Google" button
2. Google authentication completes
3. System finds the user account associated with the Google email
4. User session is established
5. User is redirected to their profile page

## Administrator Authentication Flow

### Admin Identification
Administrators are identified by their email addresses, which must be listed in the `ADMIN_EMAILS` environment variable (comma-separated list).

### Admin via Google Sign-In (First-time)
1. Admin clicks "Sign in with Google" button
2. Google authentication completes
3. System checks if the email is in `ALLOWED_EMAILS` list
4. If email is authorized:
   - A new admin record is created in the admin collection if not already present
   - Admin is redirected to the admin dashboard at `/admin`
5. If email is not authorized:
   - User is treated as a regular user and is redirected to user profile page.

### Admin via Google Sign-In (Returning)
1. Admin clicks "Sign in with Google" button 
2. Google authentication completes
3. System checks if the email is in `ALLOWED_EMAILS` and confirms admin record exists
4. Admin is redirected to the admin dashboard

### Admin via Traditional Login
1. Admin enters username and password
2. System validates credentials
3. System checks if the associated email is in `ALLOWED_EMAILS`
4. If admin privileges confirmed:
   - Admin record is created if first time login
   - Admin is redirected to the admin dashboard
5. Otherwise, user is treated as a regular user

## Session Management

- User sessions store:
  - `username`: For regular user identification
  - `email`: For admin authorization checks
  - `google_id`: For Google authentication 

- Admin sessions additionally maintain:
  - `name`: Admin's full name from Google profile
  - Google-related authentication tokens

## Logout Flow

- User/Admin navigates to `/logout`
- All session data is cleared
- User is redirected to login page

## Important Security Notes

1. Admin access is determined by the email address being present in the `ADMIN_EMAILS` environment variable
2. Google authentication is used to verify the admin's identity
3. The application checks two conditions for admin access:
   - Email is in the allowed list
   - Admin record exists in the admin collection
4. Regular users cannot access admin routes (`/admin/*`)
5. Access to protected routes is controlled by the `role_required` decorator

## Environment Configuration

The application requires these environment variables:
- `GOOGLE_CLIENT_ID`: OAuth client ID
- `GOOGLE_CLIENT_SECRET`: OAuth client secret 
- `ADMIN_EMAILS`: Comma-separated list of admin email addresses

## Error Handling

- If Google account uses an unregistered email: Account creation prompt
- If traditional login is attempted for Google-linked account: Error message directing to Google Sign-In
- If admin access is attempted with unauthorized email: 403 Access Denied page