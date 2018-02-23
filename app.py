from flask import Flask, request
from collections import Counter
import os
import socket
import numpy as np # linear algebr
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import pandas as pd
from random import randint
import json
import pyrebase

app = Flask(__name__)

config = {
  "apiKey": "AIzaSyAYgX0LDDKOXENgVHQU3WV90oCBlNeUmPE",
  "authDomain": "metro-data-mining.firebaseapp.com",
  "databaseURL": "https://metro-data-mining.firebaseio.com",
  "storageBucket": "metro-data-mining.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
# Get a reference to the auth service
auth = firebase.auth()

# Log the user in
user = auth.sign_in_with_email_and_password('metrodatamining@code.berlin', 'test123')

inputparams = ['client','product','location']

answerfile = open('answers.json','r')	# Open Intent Json File and read it into a Dictionary
answers = json.load(answerfile)
answerfile.close()

intentfile = open('intents.json','r')	# Open Intent Json File and read it into a Dictionary
intents = json.load(intentfile)
intentfile.close()

inventory = db.child("0").child("products").get(user['idToken']).val()

def instock(product,store_name):
	if product['stock'] == 'Yes':
		answ = answers[3]
	else:
		answ = answers[4]
	return answ['answers'][randint(0,1)].replace("{Product}",product['name']).replace("{Location}",store_name)

def discount(product,store_name):
	if product['promotion'] == 'Yes':
		answ = answers[7]
	else:
		answ = answers[8]
	return answ['answers'][randint(0,1)].replace("{Product}",product['name']).replace("{Location}",store_name).replace("{Price}",str(product['price']))

def openinghours(store_name):
	hours = db.child("0").child("openingHours").get(user['idToken']).val() 
	return answers[9]['answers'][randint(0,1)].replace("{Location}",store_name).replace("{hours}",hours)

def matchprodcuct(inp_product):
	inp_product_list = inp_product.lower().split(" ")
	match_products = []
	test = []
	for input_product in inp_product_list:
		for product in inventory:
			product_str = product['name'].lower().split(" ")
			for product_part in product_str:
				test.append([product_part])
				if input_product == product_part:
					match_products.append(product['id'])
	if len(match_products) != 0:
		final_product = Counter(match_products).most_common()[0][0]
		return final_product
	else:
		return 


@app.route("/")
def hello():
	input = {}
	for param in inputparams:
		input[param] = request.args.get(param)
	
	store_name = str(db.child("0").child("storeName").get(user['idToken']).val()) 
	
	if input['client'] == 'stock' or input['client'] == 'discount':
		product_id = matchprodcuct(input['product'])
		if not input['product']:
			qs = "We are sorry but we couldn't find this product."
		else:
			input['product'] = db.child("0").child("products").child(str(product_id - 1)).get(user['idToken']).val()
			if input['client'] == 'stock':
				qs = instock(input['product'], store_name)
			elif input['client'] == 'discount':
				qs = discount(input['product'], store_name)
	elif input['client'] == 'hours':
		qs = openinghours(store_name)
	else:
		qs = answers[19]['answers'][randint(0,1)]
	return qs

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

