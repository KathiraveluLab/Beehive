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
    - Update your Google Cloud Console to include the new redirect URI: ```http://localhost:5000/login/google/callback```

8. **Update `.env` File**
    - Open the `.env` file and add the required credentials.
    ```
    MONGODB_CONNECTION_STRING=mongodb://...
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    REDIRECT_URI=http://localhost:5000/admin/login/callback
    ADMIN_EMAILS=admin1@example.com,admin2@example.com
    ```
    NOTE: Add or modify the ADMIN_EMAILS variable with comma-separated emails.
9. **Run the Application**
    - Execute the `app.py` file to run the application.
    ```bash
    python app.py
    ```
## Directory Structure
The application expects certain directories to exist for proper operation:
- `static/uploads` - For general file uploads
- `static/uploads/profile` - For user and admin profile photos
- `static/uploads/thumbnails` - For PDF thumbnails

These directories will be created automatically if they don't exist, but for proper deployment you may want to ensure they're included in your repository or created during setup.

10. **Setup Guide for Running Flask with MongoDB in Docker**

This guide will help you set up and run your **Flask application with MongoDB** inside Docker using `docker-compose`.

---

## **Prerequisites**
Before you begin, ensure you have installed:
- **Docker**: [Download here](https://www.docker.com/get-started)

---

 - Run the following command to **build and start** the containers:
```sh
docker-compose up --build
```

 This will start both **Flask** and **MongoDB**.  
 Flask will be available at `http://localhost:5000`.  
 MongoDB will run inside Docker and be accessible on **port 27017**.

---

 - ## ** Verify MongoDB**
To check if MongoDB is running inside Docker:

```sh
docker ps
```

To enter the MongoDB container and check data:

```sh
docker exec -it mongodb mongosh
```

If you want to use **MongoDB Compass**, connect to:

```
mongodb://localhost:27017
```

---

 - ## ** Stopping the Containers**
To **stop** the containers:

```sh
docker-compose down
```

This will stop and remove the containers, but **data will persist** due to the volume (`mongo-data`).

---

## **RUN command**
You have successfully set up **Flask with MongoDB in Docker**!  
Now, every time you want to run your project, just use:

```sh
docker-compose up
```

By following these steps, you will have the project set up and ready to use.