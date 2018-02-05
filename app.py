from flask import Flask, request
import os
import socket

app = Flask(__name__)

@app.route("/")
def hello():
    input = request.args.get('input')
    return input 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
