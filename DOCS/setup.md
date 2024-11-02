## If you are looking for setup this project.
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
    - Activate the virtual environment.
    # Windows
    .\venv\Scripts\activate

    # Unix/MacOS
    source venv/bin/activate

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

8. **Update `.env` File**
    - Open the `.env` file and add the required credentials.
    ```
    MONGODB_CONNECTION_STRING=mongodb://...
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    REDIRECT_URI=http://localhost:5000/admin/login/callback
    ADMIN_EMAILS=admin1@example.com,admin2@example.com
    ```

9. **Run the Application**
    - Execute the `app.py` file to run the application.
    ```bash
    python app.py
    ```

By following these steps, you will have the project set up and ready to use.