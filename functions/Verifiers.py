import re
from models.users import login_user

class config_pass:

	def __init__(self):
		self.min_length = 6
		self.need_number = False
		self.need_uppercase = False
		self.need_lowercase = False
		self.need_symbol = False

	def get_min_length(self):
		return self.min_length

	def get_need_number(self, pass_):
		if self.need_number:
			return (re.search(r"\d", pass_) is None)
		return False

	def get_need_uppercase(self, pass_):
		if self.need_uppercase:
			return (re.search(r"[A-Z]", pass_) is None)
		return False 
	
	def get_need_lowercase(self, pass_):
		if self.need_lowercase:
			return (re.search(r"[a-z]", pass_) is None)
		return False

	def get_need_symbol(self, pass_):
		if self.need_symbol:
			return (re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', pass_) is None)
		return False


def verify_pass_conditions(pass_):
	c = config_pass()
	if (len(pass_) < c.get_min_length()):
		# Checking the length
		return False , "The new password contains less than 6 characters"
	elif c.get_need_number(pass_):
		# Searching for digits
		return False , "Must contain at least one number"
	elif c.get_need_symbol(pass_):
		# Searching for symbols
		return False , "Must contain at least one symbol"
	elif c.get_need_lowercase(pass_):
		# Searching for lowercase
		return False , "Must contain at least one lowercase"
	elif c.get_need_uppercase(pass_):
		# Searching for uppercase
		return False , "Must contain at least one uppercase"
	else:
		# All ok
		return True, ""

def verify_new_pass(user_, old_pass, new_pass1, new_pass2):
	c = config_pass()
	if (new_pass1 != new_pass2):
		# Checking the new passwords
		return False , "The new passwords doesn't match"
	elif not (login_user(user_, old_pass)):
		# Checking password 
		return False , "The old password is not correct"
	elif (len(new_pass1) < c.get_min_length()):
		# Checking the length
		return False , "The new password contains less than 6 characters"
	elif c.get_need_number(new_pass1):
		# Searching for digits
		return False , "Must contain at least one number"
	elif c.get_need_symbol(new_pass1):
		# Searching for symbols
		return False , "Must contain at least one symbol"
	elif c.get_need_lowercase(new_pass1):
		# Searching for lowercase
		return False , "Must contain at least one lowercase"
	elif c.get_need_uppercase(new_pass1):
		# Searching for uppercase
		return False , "Must contain at least one uppercase"
	else:
		# All ok
		return True, ""

def validemail(email):
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
    if match == None:
        return False
    else:
        return True