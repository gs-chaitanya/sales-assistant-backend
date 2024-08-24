from flask import Flask, request, jsonify
from flask_cors import CORS

import pandas as pd
import numpy as np
import os
import google.generativeai as genai
from google.generativeai import caching
import datetime
import time

import os
from dotenv import load_dotenv
load_dotenv()

import json
# with open('secrets.json', 'r') as f:
#     config = json.load(f)
# f.close()
API_key = os.getenv('API_key')

genai.configure(api_key=API_key)

file_name = "README.txt"
file  = genai.upload_file(path=file_name)

print("generating cache tokens now")

cache = caching.CachedContent.create(
    model="models/gemini-1.5-flash-001",
    display_name="Home Depot Product Catalog", 
    system_instruction="You are a sales assistant, your job is to answer customer queries and supplement it wth relevant technical information from the csv document provided. \
        additionally, also display set of display a set of short conscise bullet points for guiding the speech of a sales agent from the information you generated \
        use the following json format for output - only output plain json: \
            {\"dialogue\": \"\", \"pointers\": [\"\",\"\"]} ",

    contents=[file],
    ttl=datetime.timedelta(minutes=15),
)

# create the model
model = genai.GenerativeModel.from_cached_content(cached_content=cache)

print("model created")

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/reply', methods=["POST", "GET"])
def reply():

    api_data = request.json
    prompt = api_data.get('prompt')

    if prompt is not None:
        response = model.generate_content(prompt)
        relevant = response.text[8:-4]
        return jsonify(relevant), 200
    else:
        return jsonify({"error": "Invalid data"}), 400
    


if __name__ == '__main__':
    # app.run(host='0.0.0.0',debug=True)
    app.run(debug=True)