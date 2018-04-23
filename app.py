from flask import Flask, request
from collections import Counter
import os
import socket
import numpy as np # linear algebr
from random import randint
import json
import pyrebase
from Chatbot import Chatbot
from algoliasearch import algoliasearch

app = Flask(__name__)

client = algoliasearch.Client("ZFM0QHO6CJ", 'a0c165db0399708ee07361211ccdcfbb')
index = client.init_index('products')

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
#user = auth.sign_in_with_email_and_password('metrodatamining@code.berlin', 'test123')

answerfile = open('answers.json','r')	# Open Intent Json File and read it into a Dictionary
answers = json.load(answerfile)
answerfile.close()

def instock(product,store):
	if product['stock'] == 'Yes':
		answ = answers[3]
	else:
		answ = answers[4]
	return answ['answers'][randint(0,1)].replace("{Product}",product['name']).replace("{Location}",store['storeName'])

def discount(product,store):
	if product['promotion'] == 'Yes':
		answ = answers[7]
	else:
		answ = answers[8]
	return answ['answers'][randint(0,1)].replace("{Product}",product['name']).replace("{Location}",store['storeName']).replace("{Price}",str(product['price']))

def openinghours(store):
	hours = db.child(store['id']).child("openingHours").get().val() 
	return answers[9]['answers'][randint(0,1)].replace("{Location}",store['storeName']).replace("{hours}",hours)

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
	store_data = db.get().val()
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
	store_data = db.get().val()
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

@app.route("/")
def hello():
	input_string = request.args.get('string')
	
	chatbot = Chatbot()
	input = chatbot.process_message(input_string)

	if not input['location']:
		store = db.child("0").get().val() 
	else:
		store = match_location(input['location'])

	if input['client'] == 'stock' or input['client'] == 'sale' or input['client'] == 'description':
		if not input['product'] or input['product'] == '':
			qs = "We are sorry but you have to give us a product name."
		else:
			res = index.search(input['product'], {"hitsPerPage": 1})
			if len(res['hits']) > 0:
				input['productid'] = res['hits'][0]['objectID']
				input['product'] = res['hits'][0]['name']
				input['product'] = db.child(store['id']).child("products").child(input['productid']).get().val()
				
				if input['client'] == 'stock':
					qs = instock(input['product'], store)
				elif input['client'] == 'sale':
					qs = discount(input['product'], store)
				elif input['client'] == 'description':
					qs = description(input['product'], input['description'])
			else:
				qs = "We are sorry but we couldn't find this product."
	elif input['client'] == 'hours':
		if store:
			qs = openinghours(store)
		else:
			qs = "We are sorry but we couldn't find this store?"
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
