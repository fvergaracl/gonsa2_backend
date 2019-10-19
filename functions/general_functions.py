import bcrypt
import hashlib, binascii
import random, string
import base64
import os 
UPLOAD_FOLDER = '/var/www/api_gonsa2/static/uploads/'

def random_salt():
    return bcrypt.gensalt()

def encrypt_pass(passw , salt):
	dk = hashlib.pbkdf2_hmac('sha256', passw, salt, 9503)
	return binascii.hexlify(dk)

def get_random(number):
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(number))

def get_random_num(number):
    return ''.join(random.choice(string.digits) for x in range(number))

def get_random_str(number):
    return ''.join(random.choice(string.ascii_letters) for x in range(number))

def convert_and_save_image(b64_string, user_, class_):
	try:

		imagenbase64 = b64_string[b64_string.find(",")+1:]
		image_url = get_random(10)
		if not os.path.exists(UPLOAD_FOLDER +class_):
			os.makedirs(UPLOAD_FOLDER +class_)
		if not os.path.exists(UPLOAD_FOLDER + str(class_+'/'+user_)):
			os.makedirs(UPLOAD_FOLDER +str(class_+'/'+user_))

		with open(UPLOAD_FOLDER+ str(class_+'/'+user_+'/'+image_url)+".png", "wb+") as fh:
			fh.write(base64.decodestring(imagenbase64.encode('ascii')))
		return str('static/uploads/'+class_+'/'+user_+'/'+image_url)+".png"
	except Exception as e:
		print e
    

def search_term_bing(query):
	import requests
	import json
	
	subscription_key = 'b3d290afca044f65bc0601f2fbf5df04'
	#Key1: b3d290afca044f65bc0601f2fbf5df04
	#Key2: cd7124bd63674919b13d8702f656124e
	assert subscription_key
	search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
	#https://api.cognitive.microsoft.com/bing/v7.0/search[?q][&count][&offset][&mkt][&safesearch]
	#https://dev.cognitive.microsoft.com/docs/services/f40197291cd14401b93a478716e818bf/operations/56b4447dcf5ff8098cef380d
	headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
	params  = {"q": query, "count":50, "textDecorations":True, "textFormat":"HTML"}
	response = requests.get(search_url, headers=headers, params=params)
	response.raise_for_status()
	return response.json()

class MyException(Exception):
    pass

