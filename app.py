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

inputparams = ['client','product','location', 'product_key_words']

answerfile = open('answers.json','r')	# Open Intent Json File and read it into a Dictionary
answers = json.load(answerfile)
answerfile.close()

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

def description(product, product_key_words):
	product_description = product['description'].lower().split(", ")
	answ = ""
	for item in product_description:
		if item == product_key_words:
			answ = answers[5]
	if answ == "":
		answ = answers[6]
	return answ['answers'][randint(0,1)].replace("{Product}", product['name']).replace("{Description}", product_key_words)

def get_all_locations():
	store_data = db.get(user['idToken']).val()
	store_list = []
	store_amount = 0
	for store in store_data:
		store_list.append(store['storeName'])
		store_amount += 1
	if len(store_list) > 1:
		last_store = store_list.pop()
		output_string = ', '.join(store_list) + " and " + last_store
	else:
		output_string = store_list[0]
	return answers[10]['answers'][randint(0,1)].replace("{Location}", output_string).replace('{LocationAmount}', str(store_amount))

def match_location(location):
	store_data = db.get(user['idToken']).val()
	for store in store_data:
		if store['storeName'].lower() == location.lower():
			return store
	return

def get_location(location, client):
	store = match_location(location)
	if store:
		if client == 'location':
			answ = answers[11]
		else:
			answ = answers[13]
		location = store['storeName']
		address = store['address']
	else:
		answ = answers[12]
		address = ""
	return answ['answers'][randint(0,1)].replace("{Location}", location).replace("{Address}", address)

def matchproduct(inp_product):
	inp_product_list = inp_product.lower().split(" ")
	match_products = []
	for input_product in inp_product_list:
		for product in inventory:
			product_list = product['name'].lower().split(" ")
			for product_part in product_list:
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
	
	if input['client'] == 'stock' or input['client'] == 'discount' or input['client'] == 'description':
		product_id = matchproduct(input['product'])
		if not product_id:
			qs = "We are sorry but we couldn't find this product."
		else:
			input['product'] = db.child("0").child("products").child(str(product_id - 1)).get(user['idToken']).val()
			if input['client'] == 'stock':
				qs = instock(input['product'], store_name)
			elif input['client'] == 'discount':
				qs = discount(input['product'], store_name)
			elif input['client'] == 'description':
				qs = description(input['product'], input['product_key_words'])
	elif input['client'] == 'hours':
		qs = openinghours(store_name)
	elif input['client'] == 'all_locations':
		qs = get_all_locations()
	elif input['client'] == 'location' or input['client'] == 'address':
		if input['location']:
			qs = get_location(input['location'], input['client'])
		else:
			qs = 'You didnt give us a location'
	else:
		qs = answers[19]['answers'][randint(0,1)]
	return qs

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

