import os

def is_admin_email(email: str) -> bool:
    admins = os.getenv("ADMIN_EMAILS", "")
    admin_list = [e.strip().lower() for e in admins.split(",") if e.strip()]
    return email.lower() in admin_list
