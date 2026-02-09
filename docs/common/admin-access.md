# Grant Admin Access for Local Development

 Admin access for local development can be configured in one of two ways:

 - Add the admin email addresses to the `ADMIN_EMAILS` variable in your `.env`. Users created with those emails will be assigned the `admin` role by the backend utilities.
 - Or, directly update the `role` field of a user document in the local MongoDB `users` collection to `"admin"`.

 Notes:
 - This admin access is for local development only and uses your local database.
 - After changing a user's role, logout and log in again to get a fresh access token with the updated role.
 - Admin dashboard URL: `http://localhost:5173/admin`

