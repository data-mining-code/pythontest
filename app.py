from flask import Flask, request
from collections import Counter
import os
import socket
import numpy as np # linear algebr
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import pandas as pd
import json

app = Flask(__name__)

intentfile = open('intents.json','r')	# Open Intent Json File and read it into a Dictionary
intents = json.load(intentfile)
intentfile.close()

@app.route("/")
def hello():
	input = request.args.get('input')		# Get Input from Broker
	input_list = input.lower().split(" ")	# Make the input lowercase
	query = {}
	for word in input_list:
		for intent in intents:
			for iword in intent['words']:
				test = iword.split(" ")
				for iw in test:
					if word == iw and intent['tag'] in query.keys():
						query[intent['tag']].append(iword)
					elif word == iw:
						query[intent['tag']] = [iword] 
	for key in query.keys():
		query[key] = Counter(query[key]).most_common()[0][0]
	return json.dumps(query)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

