# Project Setup

## Prerequisites
- Python 3.x
- MongoDB
- Google OAuth2 credentials

## Setup Instructions

Follow these steps to set up the project:

> **Note:** For Docker-based setup, see [docker-setup.md](docker-setup.md)

1. **Clone the Beehive Repository**
    - Clone the Beehive repository to your local machine.
    ```bash
    git clone https://github.com/kathiravelulab/Beehive.git'
    cd Beehive
    ```

2. **Install and MongoDB**
    - Make sure MongoDB is installed and is currently running.
    - In Linux, the command to check the status is:
   ```bash
    sudo systemctl status mongod
    ```
    You should see a status, such as:
    ```bash
     mongod.service - MongoDB Database Server
     Loaded: loaded (/usr/lib/systemd/system/mongod.service; enabled; preset: enabled)
     Active: active (running) since Fri 2025-10-10 05:40:36 AKDT; 58min ago
       Docs: https://docs.mongodb.org/manual
     Main PID: 1665 (mongod)
     Memory: 257.1M (peak: 345.8M)
     CPU: 13.341s
     CGroup: /system.slice/mongod.service
             └─1665 /usr/bin/mongod --config /etc/mongod.conf
     Oct 10 05:40:36 Llovizna systemd[1]: Started mongod.service - MongoDB Database Server.
     Oct 10 05:40:46 Llovizna mongod[1665]: {"t":{"$date":"2025-10-10T13:40:46.804Z"},"s":"I",  "c":"CONTROL",  "id":7484500, "ctx":"main","msg":"Environment variable MONGODB_CONFIG_OVERRI>
    ```

3. **Create a Virtual Environment**
    - Navigate to the project directory and create a virtual environment.
    ```bash
    python -m venv venv
    ```

4. **Activate the Virtual Environment**
   
    ***Windows***
    ```bash
    .\venv\Scripts\activate
    ```

    ***Unix/MacOS***
    ```bash
    source venv/bin/activate
    ```

5. **Install Required Libraries**
    - Install all the libraries listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

6. **Configure Environment Variables**
    - Rename `.env.example` to `.env`.

7. **Create Google OAuth API Key**
    - Create a Google OAuth API key.
    - Download the `client_secret.json` file and place it in the Beehive project/root directory.
    - Update your Google Cloud Console to include the new redirect URI: ```http://localhost:5000/login/google/callback```


8. **Set Up Clerk Authentication and create Clerk Keys**
    - Sign up for a Clerk account at [https://clerk.dev](https://clerk.dev)
    - Log in to Clerk and go to Clerk Dashboard
    - Create a new application in Clerk
    - Copy your Publishable Key and Secret Key from Clerk and update your `.env` file.
    - Copy Clerk Frontend API URL to CLERK_ISSUER in your `.env` file.
    - Navigate to **Configure**.
    - Select **Sessions** under **Session Management**.
    - Add the following inside **Claims** and save the changes:
    ```
    {
      "role": "{{user.public_metadata.role || 'user'}}"    
    }
    ```
      
      
9. **Grant Admin Access for Local Development**

    **Prerequisite:** Make sure you've completed Step 8 and configured the session claim in Clerk Dashboard (Configure → Sessions → Claims). The session claim must include `{"role": "{{user.public_metadata.role || 'user'}}"}` for the role to be included in JWT tokens.

    For detailed step-by-step instructions on how to grant admin access, see [Admin Access Guide](common/admin-access.md).

10. **Update `.env` File** 

    Open the `.env` file and add the required credentials. **All environment variables below are mandatory** for the application to function properly.

    **Note: Add or modify the ADMIN_EMAILS variable with comma-separated emails. Make sure there are no spaces before or after the commas.**

    ```bash
    # Database Configuration (Required)
    MONGODB_CONNECTION_STRING=mongodb://...

    # Google OAuth Configuration (Required for Google authentication)
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    REDIRECT_URI=http://localhost:5000/admin/login/callback

    # Admin Configuration (Required for admin access)
    ADMIN_EMAILS=admin1@example.com,admin2@example.com

    # Clerk Authentication (REQUIRED - App will not start without this)
    CLERK_SECRET_KEY=your_clerk_secret_key

    # Flask Security (Optional - defaults to 'beehive' if not set)
    FLASK_SECRET_KEY=your_custom_flask_secret

    # CORS Configuration (Optional - defaults to common development origins if not set)
    # Format: comma-separated list of allowed origins (e.g., http://localhost:5173,https://example.com)
    CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
    ```

    #### 🌐 **About CORS_ORIGINS:**
    - This variable specifies which frontend origins are allowed to make requests to the backend API
    - Format: comma-separated list of URLs (no spaces around commas, or spaces will be automatically trimmed)
    - If not set, defaults to common development origins (localhost:5173 and localhost:3000)
    - For production, add your production frontend URL(s)
    - Example: `CORS_ORIGINS=http://localhost:5173,https://yourdomain.com`

    #### 🔑 **Finding Your CLERK_SECRET_KEY:**
    1. Go to your [Clerk Dashboard](https://dashboard.clerk.dev/)
    2. Select your application
    3. Navigate to "API Keys" in the sidebar
    4. Copy the **Secret key** (starts with `sk_`)
    5. Paste it as the value for `CLERK_SECRET_KEY` in your `.env` file

    #### **Important Notes:**
    - **CLERK_SECRET_KEY is mandatory**: The application will fail to start with a `ValueError` if this is missing
    - **No quotes needed**: Environment variable values should not be wrapped in quotes
    - **Keep it secure**: Never commit your `.env` file to version control (it's already in `.gitignore`)

    #### 🔧 **Troubleshooting:**
    If you see errors like:
    - `ValueError: Missing required environment variable: CLERK_SECRET_KEY`
    - `Config validation failed`

    Make sure your `.env` file contains all required variables and restart the application.
   
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    REDIRECT_URI=http://localhost:5000/admin/login/callback

    ### Admin Configuration (Required for admin access)
    ADMIN_EMAILS=admin1@example.com,admin2@example.com

    ### Clerk Authentication (REQUIRED - App will not start without this)
    CLERK_SECRET_KEY=your_clerk_secret_key

    ### Flask Security (Optional - defaults to 'beehive' if not set)
    FLASK_SECRET_KEY=your_custom_flask_secret

    #### 🔑 **Finding Your CLERK_SECRET_KEY:**
    1. Go to your [Clerk Dashboard](https://dashboard.clerk.dev/)
    2. Select your application
    3. Navigate to "API Keys" in the sidebar
    4. Copy the **Secret key** (starts with `sk_`)
    5. Paste it as the value for `CLERK_SECRET_KEY` in your `.env` file

    #### **Important Notes:**
    - **CLERK_SECRET_KEY is mandatory**: The application will fail to start with a `ValueError` if this is missing
    - **No quotes needed**: Environment variable values should not be wrapped in quotes
    - **Keep it secure**: Never commit your `.env` file to version control (it's already in `.gitignore`)

    #### 🔧 **Troubleshooting:**
    If you see errors like:
    - `ValueError: Missing required environment variable: CLERK_SECRET_KEY`
    - `Config validation failed`

    Make sure your `.env` file contains all required variables and restart the application.
   
11. **Run the backend**
    - Execute the `app.py` file to run the application.
    ```bash
    python app.py
    ```

    This sets up the backend.

12. **Configure the frontend**
    - Install the frontend dependencies.
    ```bash
    cd frontend
    npm install
    ```

    - Create a `.env` file in the frontend directory and add your Clerk publishable key:
    ```
    VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
    ```

13. **Run the frontend**
    - Add .env file in the frontend folder.

    ```
    VITE_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
    ```
    
    - Run the following commmands to start the development server:
     ```bash
    npm run dev
     ```

14. **Confirm the App is working.**
    - Open [http://localhost:5173](http://localhost:5173) to view the app in your browser.
    
By following these steps, you will have the project set up and ready to use.