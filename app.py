from flask import Flask, request
import os
import socket
import numpy as np # linear algebr
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import pandas as pd
import json

app = Flask(__name__)

fifa = pd.read_csv("CompleteDataset.csv", skipinitialspace=True)
fifa = fifa.drop('Unnamed: 0', axis=1)

intentfile = open('intents.json','r')	# Open Intent Json File and read it into a Dictionary
intents = json.load(intentfile)
intentfile.close()

@app.route("/")
def hello():
    input = request.args.get('input')		# Get Input from Broker
    if input == "How many players are in FiFa18?":				# These are the proof of Concept questions for mentor meeting on 13.02. These proof 
    	return 'There are ' + str(len(fifa)) + ' Players in FiFa18'   # ... of concept questions can't be handled like the normal intents  
    elif input == "How much does Ronaldo cost?":						# This can be deleted after 13.02
    	return "Ronaldo is worth " + str(fifa[fifa.Name == 'Cristiano Ronaldo']['Value'].values[0]) + " Euro" 
    else:														# Here starts the processing for the normal intents
    	input_list = input.lower().split(" ")					# Make the input lowercase and split it into the words
    	if '?' in input_list[-1] and len(input_list[-1]) > 1: input_list[-1] = input_list[-1][:-1]		# checks if in the last element a word and a '?' and removes the ?
    	query = {} 
    	for word in input_list:
    		for intent in intents:
    			for iword in intent['words']:
    				if word == iword:
    					query[intent['tag']] = word
    	return json.dumps(query) 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

