import string


def is_valid_username(username):
  
  if not username:
    return False 

  allowed_chars = string.ascii_letters + string.digits + "_-."
  min_length, max_length = 4, 25

  if not (min_length <= len(username) <= max_length):
    return False 


  if username.isalpha() or username.isdigit() or all(char in ("_", "-", ".") for char in username):
    return False  

  return all(char in allowed_chars for char in username)