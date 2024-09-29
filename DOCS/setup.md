## If you are looking for setup this project.
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
    ```bash
    # On Windows
    .\venv\Scripts\activate

    # On macOS/Linux
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

8. **Update `.env` File**
    - Open the `.env` file and add the required credentials.

9. **Run the Application**
    - Execute the `app.py` file to run the application.
    ```bash
    python app.py
    ```

By following these steps, you will have the project set up and ready to use.