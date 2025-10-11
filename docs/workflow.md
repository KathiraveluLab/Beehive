## Workflows

### 1) Login 
1. The Login and authentication are supported by Clerk

### 2) User Upload Media
1. User submits form to `POST /api/user/upload/{user_id}` with files, title, description, optional `audioData` and `sentiment`.
2. Backend validates inputs and allowed extensions.
3. Files saved to `static/uploads/`; optional audio decoded from base64 and saved.
4. MongoDB `images` document inserted.
5. Admin `notifications` document inserted.
6. If PDF, generate thumbnail to `static/uploads/thumbnails/`.

### 3) Edit Media
1. Owner hits `POST /edit/{image_id}` with new `title`, `description`, optional `sentiment`.
2. Backend finds image and updates fields in MongoDB.

### 4) Delete Media
1. Owner hits `GET /delete/{image_id}`.
2. Backend deletes file from `static/uploads/`, removes audio and PDF thumbnail if exist.
3. Deletes MongoDB image document.

### 5) View User Uploads
1. Client calls `GET /api/user/user_uploads/{user_id}`.
2. Backend returns list of images for the user.

### 6) Admin Dashboard Data
1. Client calls `GET /api/admin/dashboard`.
2. Backend computes stats from `images` and fetches recent uploads.
3. Enhances user info by calling `GET /api/admin/users` (Clerk REST under the hood).

### 7) Notifications
1. Admin client calls `GET /api/admin/notifications?mark_seen=true` to fetch unseen and mark them seen.

### 8) Admin Users Listing
1. Admin client calls `GET /api/admin/users` with optional search, limit, offset.
2. Backend calls Clerk API with `CLERK_SECRET_KEY` and transforms the response.

### 9) Chat Messages
1. Client posts a message to `POST /api/chat/send`.
2. Backend persists into `messages` collection with timestamp.
3. Client fetches conversation via `GET /api/chat/messages?user_id={id}&with_admin=true`.



