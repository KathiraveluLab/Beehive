# Grant Admin Access for Local Development

To access the admin dashboard in your local development environment, you need to set the admin role in your Clerk user account.

**Prerequisite:** Make sure you've configured the session claim in Clerk Dashboard (Configure → Sessions → Claims). The session claim must include `{"role": "{{user.public_metadata.role || 'user'}}"}` for the role to be included in JWT tokens.

## Steps to Grant Admin Access

1. Go to [Clerk Dashboard](https://dashboard.clerk.dev/)
2. Navigate to **Users** (not Organizations)
3. Find your user account (search by your email address)
4. Click on your user profile to open it
5. Navigate to the **Metadata** section
6. Under **Public metadata**, add or update the following:
   ```json
   {
     "role": "admin"
   }
   ```
7. Click **Save** to apply the changes

## Important Notes

- This admin access is for **local development only** and uses your local database
- Your local MongoDB data is separate from production
- After setting the role, **logout and login again** from the application to refresh your session token
- You can verify your role by checking the browser console:
  ```javascript
  // After login, check in browser console
  console.log(user?.publicMetadata?.role)
  // Should show: "admin"
  ```

## Accessing Admin Dashboard

- Once the role is set and you've logged in again, navigate to `http://localhost:5173/admin`
- You should now have access to:
  - Admin Dashboard (`/admin`)
  - User Management (`/admin/users`)
  - Analytics (`/admin/analytics`)

