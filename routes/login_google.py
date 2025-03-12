from flask import session, redirect, Blueprint
from google_auth_oauthlib.flow import Flow
import os
import pathlib

client_secrets_file = os.path.join(pathlib.Path(__file__).parent.parent, "client_secret.json")

google_login = Blueprint('google_login', __name__)


@google_login.route('/login/google')
def login_google():
    # Create a flow instance for user authentication
    user_flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri="http://127.0.0.1:5000/login/google/callback"
    )
    
    authorization_url, state = user_flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)