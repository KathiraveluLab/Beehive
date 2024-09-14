import re
import string



def is_valid_username(username):
  
  if not username:
    return False 

  min_length, max_length = 4, 25

  if not (min_length <= len(username) <= max_length):
    return False 
  
  return True

