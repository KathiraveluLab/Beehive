## API Documentation

All responses are JSON unless otherwise noted. CORS is enabled for local development with credentials.

Base URL (dev): `http://127.0.0.1:5000`

### Authentication & Authorization
- User & Admin endpoints may rely on application session or be called from the frontend with user context.

---

### User Uploads

#### POST `/api/user/upload/{user_id}`
- **Description**: Upload one or more images or PDFs, with optional audio data.
- **Auth**: Logged-in user.
- **Content-Type**: `multipart/form-data`
- **Form fields**:
  - `username` (string)
  - `files` (file[]) multiple files allowed; allowed: jpg, jpeg, png, gif, webp, heif, pdf
  - `title` (string, required)
  - `description` (string, required)
  - `sentiment` (string, optional)
  - `audioData` (base64 data URL, optional)
- **Responses**:
  - 200: `{ message: "Upload successful" }`
  - 400: `{ error: "..." }` (e.g., missing required fields, disallowed file type)
  - 500: `{ error: "Error uploading file: ..." }`

Side effects:
- Saves files to `static/uploads/`.
- Generates PDF thumbnail for `.pdf` as `.jpg` in `static/uploads/thumbnails/`.
- Inserts `image` record and admin `notification` in MongoDB.

---

### Image Management

#### PATCH `/edit/{image_id}`
- **Description**: Update title, description, and optionally sentiment for an image.
- **Auth**: Owner (or admin).
- **Content-Type**: `application/x-www-form-urlencoded` or `multipart/form-data`
- **Fields**: `title` (required), `description` (required), `sentiment` (optional)
- **Responses**:
  - 200: `{ message: "Image updated successfully!" }`
  - 400: `{ error: "Invalid image ID format: ..." }` or validation errors
  - 404: `{ error: "Image not found." }`
  - 500: `{ error: "Error updating image: ..." }`

#### DELETE `/delete/{image_id}`
- **Description**: Delete image, associated audio, and PDF thumbnail (if any), and remove DB record.
- **Auth**: Owner (or admin).
- **Responses**:
  - 200: `{ message: "Image deleted successfully!" }`
  - 400/404/500 on errors

#### GET `/api/user/user_uploads/{user_id}`
- **Description**: List images uploaded by a user.
- **Auth**: Owner or admin.
- **Responses**:
  - 200: `{ images: [{ id, filename, title, description, audio_filename, sentiment, created_at }] }`
  - 500: `{ error: "..." }`

---

### Admin APIs (`/api/admin`)

#### GET `/api/admin/user_uploads/{user_id}`
- Mirrors user uploads listing but from admin context.

#### GET `/api/admin/users`
- **Description**: List users via Clerk REST API.
- **Query**: `query` (search), `limit` (default 10), `offset` (default 0)
- **Responses**:
  - 200: `{ users: [{ id, name, email, role, lastActive, image, clerkId }], totalCount }`
  - 500: `{ error: "Failed to fetch users" }`
- **Notes**: Requires env `CLERK_SECRET_KEY`. Backend calls `https://api.clerk.com/v1/users`.

#### GET `/api/admin/users/only-users`
- As above, but filters to `role === 'user'`.

#### GET `/api/admin/dashboard`
- **Description**: Returns upload statistics and recent uploads.
- **Query**: `limit` (recent uploads count; default 10)
- **Responses**:
  - 200: `{ stats: { totalImages, totalVoiceNotes, totalMedia }, recentUploads: [...] }`
  - 500: `{ error: "Failed to fetch dashboard data" }`

---

### Notifications

#### GET `/api/admin/notifications?mark_seen={true|false}`
- **Description**: Get unseen notifications; optionally mark them as seen.
- **Responses**:
  - 200: `{ notifications: [{ _id, user_id, username, image_filename, title, timestamp, seen, type }] }`
  - 500: `{ error: "..." }`

---

### Chat

#### POST `/api/chat/send`
- **Body**: JSON `{ from_id, from_role, to_id, to_role, content }`
- **Responses**:
  - 200: `{ message: "Message sent" }`
  - 400/500 on errors

#### GET `/api/chat/messages?user_id={id}&with_admin=true`
- **Description**: Fetch messages between given user and admin, sorted by timestamp asc.
- **Responses**:
  - 200: `{ messages: [{ _id, from_id, from_role, to_id, to_role, content, timestamp }] }`
  - 400/500 on errors

---

### Static Media

#### GET `/audio/{filename}`
- Serves audio file from `static/uploads/`.

---

### Status Codes
- 200 OK: Success
- 400 Bad Request: Missing or invalid input
- 401 Unauthorized: Not logged in (for protected routes)
- 403 Forbidden: No access (role mismatch)
- 404 Not Found: Resource absent
- 500 Internal Server Error: Unexpected error

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
- `PATCH /edit/<image_id>` - Edit image details
- `DELETE /delete/<image_id>` - Delete image

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

