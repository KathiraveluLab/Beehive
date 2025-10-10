# Project Setup

## Prerequisites
- Python 3.x
- MongoDB
- Google OAuth2 credentials
- IDE (VS Code recommended)

# Setup Instructions

Follow these steps to set up the project:

1. **Fork and Clone the Repository**
    - Fork the repository to your GitHub profile.
    - Clone the forked repository to your local machine.
    ```bash
    git clone https://github.com/your-username/Beehive.git
    ```

2. **Open the Project in Your IDE**
    - Open the project in your favorite IDE, such as Visual Studio Code or PyCharm.

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
    - Rename `client_secret_example.json` to `client_secret.json`.

7. **Create Google OAuth API Key**
    - Create a Google OAuth API key.
    - Download the `client_secret.json` file and place it in the project directory.
    - Update your Google Cloud Console to include the new redirect URI: ```http://localhost:5000/login/google/callback```

8. **Update `.env` File**
    - Open the `.env` file and add the required credentials.
    ```
    MONGODB_CONNECTION_STRING=mongodb://...
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    REDIRECT_URI=http://localhost:5000/admin/login/callback
    ADMIN_EMAILS=admin1@example.com,admin2@example.com
    CLERK_SECRET_KEY = your clerk secret key
    ```
    NOTE: Add or modify the ADMIN_EMAILS variable with comma-separated emails.Make sure there are no spaces before or after the commas.
   
10. **Run the backend**
    - Execute the `app.py` file to run the application.
    ```bash
    python app.py
    ```

    This sets up the backend

11. **Run the frontend**
    Add .env file in the frontend folder.

    ```
    VITE_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
    ```
    Then run the following commmands
     ```bash
    cd frontend
    npm install
    npm run dev
     ```

12. **Set Up Clerk Authentication**
    - Go to Clerk Dashboard
    - Create a New Application
    - You will get your Publishable Key and Secret Key

    
By following these steps, you will have the project set up and ready to use.
