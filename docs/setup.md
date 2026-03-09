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


8. **JWT Authentication Setup**
    - This project uses JWT access tokens issued by the backend. Configure a strong `JWT_SECRET` in your `.env` (or Docker environment).
    - Optionally set `JWT_EXPIRE_HOURS` (defaults to 24).

9. **Grant Admin Access for Local Development**

    **Prerequisite:** Admin emails are configured via `ADMIN_EMAILS` in your `.env`. Users created with those emails will be assigned the `admin` role by the backend utilities. For details, see [Admin Access Guide](common/admin-access.md).

10. **Update `.env` File** 

    Open the `.env` file and add the required credentials. **All environment variables below are mandatory** for the application to function properly.

    **Note: Add or modify the ADMIN_EMAILS variable with comma-separated emails. Make sure there are no spaces before or after the commas.**

    ```bash
    # Database Configuration (Required)
    MONGODB_URI=mongodb://localhost:27017/
    DATABASE_NAME=beehive

    # Google OAuth Configuration (Required for Google authentication)
    GOOGLE_CLIENT_ID=your_google_client_id_here
    GOOGLE_CLIENT_SECRET=your_google_client_secret_here
    GOOGLE_API_KEY=your_google_api_key_here
    REDIRECT_URI=http://localhost:5000/admin/login/callback
    
    # Email(SMTP)
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=true
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_app_password_here

    # Admin Configuration (Required for admin access)
    ADMIN_EMAILS=admin1@example.com,admin2@example.com

    # JWT Authentication
    JWT_SECRET=your_jwt_secret_here
    JWT_EXPIRE_HOURS=24

    # Flask Security (Optional - defaults to 'beehive' if not set)
    FLASK_SECRET_KEY=your_custom_flask_secret
    
    # OAuth (Development only)
    OAUTHLIB_INSECURE_TRANSPORT=1

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

    #### **Important Notes:**
    - **JWT_SECRET is mandatory**: The application will fail to start if this is missing or insecure.
    - **No quotes needed**: Environment variable values should not be wrapped in quotes
    - **Keep it secure**: Never commit your `.env` file to version control (it's already in `.gitignore`)

    #### 🔧 **Troubleshooting:**
    If you see errors like:
    - `ValueError: Missing or insecure JWT_SECRET environment variable.`
    - `Config validation failed`

    Make sure your `.env` file contains all required variables and restart the application.
   
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    REDIRECT_URI=http://localhost:5000/admin/login/callback

    ### Admin Configuration (Required for admin access)
    ADMIN_EMAILS=admin1@example.com,admin2@example.com

    ### JWT Authentication
    JWT_SECRET=your_jwt_secret_here
    JWT_EXPIRE_HOURS=24

    ### Flask Security (Optional - defaults to 'beehive' if not set)
    FLASK_SECRET_KEY=your_custom_flask_secret

    #### 🔧 **Troubleshooting:**
    If you see errors related to missing secrets or config validation, verify your `.env` and restart the application.

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

    - Frontend does not require a Clerk publishable key when using JWTs. The frontend stores the access token in `localStorage` after login.

13. **Run the frontend**
    - Run the following commands to start the development server:
     ```bash
    npm run dev
    ```

14. **Confirm the App is working.**
    - Open [http://localhost:5173](http://localhost:5173) to view the app in your browser.

By following these steps, you will have the project set up and ready to use.