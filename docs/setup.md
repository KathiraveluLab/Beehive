# Project Setup

## Prerequisites
- Python 3.x
- MongoDB
- Google OAuth2 credentials

# Setup Instructions

Follow these steps to set up the project:

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
    - Navigate to **Configure**.
    - Select **Sessions** under **Session Management**.
    - Add the following inside **Claims** and save the changes:
    ```
    {
      "role": "{{user.unsafe_metadata.role || 'user'}}"    
    }
    ```
      
9. **Update `.env` File**
    - Open the `.env` file and add the required credentials.
    - Note: Add or modify the ADMIN_EMAILS variable with comma-separated emails. Make sure there are no spaces before or after the commas.
    ```
    MONGODB_CONNECTION_STRING=mongodb://...
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    REDIRECT_URI=http://localhost:5000/admin/login/callback
    ADMIN_EMAILS=admin1@example.com,admin2@example.com
    CLERK_SECRET_KEY = your clerk secret key
    ```
   
10. **Run the backend**
    - Execute the `app.py` file to run the application.
    ```bash
    python app.py
    ```

    This sets up the backend.

11. **Configure the frontend**
    - Install the frontend dependencies.
    ```bash
    cd frontend
    npm install
    ```

    - Create a `.env` file in the frontend directory and add your Clerk publishable key:
    ```
    VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
    ```

11. **Run the frontend**
    - Add .env file in the frontend folder.

    ```
    VITE_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
    ```
    
    - Run the following commmands to start the development server:
     ```bash
    npm run dev
     ```

12. **Confirm the App is working.**
    - Open [http://localhost:5173](http://localhost:5173) to view the app in your browser.
    
By following these steps, you will have the project set up and ready to use.
