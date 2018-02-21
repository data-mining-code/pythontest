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

answerfile = open('answers.json','r')	# Open Intent Json File and read it into a Dictionary
answers = json.load(answerfile)
answerfile.close()

intentfile = open('intents.json','r')	# Open Intent Json File and read it into a Dictionary
intents = json.load(intentfile)
intentfile.close()

inventory = db.child("0").child("products").get(user['idToken']).val()

def instock(productid):
	product = db.child("0").child("products").child(str(productid - 1)).get(user['idToken']).val()
	store = db.child("0").child("storeName").get(user['idToken']).val() 
	if product['stock'] == 'Yes':
		return answers[3]['answers'][randint(0,1)].replace("{Product}",product['name']).replace("{Location}",str(store))
	else:
		return answers[4]['answers'][randint(0,1)].replace("{Product}",product['name']).replace("{Location}",str(store))

def discount(productid):
	product = db.child("0").child("products").child(str(productid - 1)).get(user['idToken']).val()
	store = db.child("0").child("storeName").get(user['idToken']).val() 
	if product['promotion'] == 'Yes':
		return answers[7]['answers'][randint(0,1)].replace("{Product}",product['name']).replace("{Location}",str(store)).replace("{Price}",str(product['price']))
	else:
		return answers[8]['answers'][randint(0,1)].replace("{Product}",product['name']).replace("{Location}",str(store)).replace("{Price}",str(product['price']))

def openinghours():
	store = db.child("0").child("storeName").get(user['idToken']).val() 
	hours = db.child("0").child("openingHours").get(user['idToken']).val() 
	return answers[9]['answers'][randint(0,1)].replace("{Location}",str(store)).replace("{hours}",hours)

@app.route("/")
def hello():
	input = {}
	
	input['client'] = request.args.get('client') 		# Get Input from Broker 



	if input['client'] == 'stock':
		input['product'] = request.args.get('product')
		input['location'] = request.args.get('location')

		





	# input_list = input.lower().split(" ")	# Make the input lowercase
	# if '?' in input_list[-1] and len(input_list[-1]) > 1: input_list[-1] = input_list[-1][:-1]
	# query = {}
	# for intent in intents:
	# 	query[intent['tag']] = []
	# query['products'] = []
	# for word in input_list:	
	# 	for intent in intents:
	# 		for iword in intent['words']:
	# 			iword_list = iword.split(" ")
	# 			for iw in iword_list:
	# 				if word == iw and intent['tag'] in query.keys():
	# 					query[intent['tag']].append(iword)
	# 	for item in inventory:
	# 		test = item['name'].lower().split(" ")
	# 		for iw in test:
	# 			if word == iw and "products" in query.keys():
	# 				query['products'].append(item['id']) 
	# for key in query.keys():
	# 	if len(query[key]) != 0:
	# 		query[key] = Counter(query[key]).most_common()[0][0]

	# if query['question_words'] == 'have' and query['question_key_words'] == 'stock' and query['products'] != []:
	# 	answer = instock(query['products'])
	# elif query['question_words'] == 'is' or query['question_words'] == 'have' and query['question_key_words'] == 'discount' and query['products'] != []:
	# 	answer = discount(query['products'])
	# elif query['question_words'] == 'when' and query['question_key_words'] == 'open' or query['question_key_words'] == 'hours':
	# 	answer = openinghours()
	# else:
	# 	answer = "Your Request couldn't be handled " + json.dumps(query)

	return json.dumps(input)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

