from flask import Flask, request
import os
import socket
import numpy as np # linear algebr
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import pandas as pd

app = Flask(__name__)

fifa = pd.read_csv("CompleteDataset.csv", skipinitialspace=True)
fifa = fifa.drop('Unnamed: 0', axis=1)

@app.route("/")
def hello():
    input = request.args.get('input')
    if input == "How many players are in FiFa18?":
    	return 'There are ' + str(len(fifa)) + ' Players in FiFa18' 
    elif input == "How much does Ronaldo cost?":
    	return "Ronaldo is worth " + str(fifa[fifa.Name == 'Cristiano Ronaldo']['Value'].values[0]) + " Euro" 
    else:
    	return "PythonTest can not handle your response" 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
