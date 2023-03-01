import json

import mysql.connector

from datetime import datetime

from flask import Flask, request, jsonify

import openai

from mysql.connector import OperationalError

from openai.api_resources import completion

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

openai.api_key = "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"

# Connect to the database
conn= mysql.connector.connect(
            host="localhost",
           database="LTIusers",
           user="root",
           password="Root@123")

# Define a cursor to execute queries
cursor = conn.cursor()
prompt = "Write a blog on ChatGPT"

# Define the login endpoint

@app.route('/login', methods=['POST'])
def login():
    cursor = conn.cursor()

    username = request.json.get('username')
    password = request.json.get('password')
    password_hash = generate_password_hash(password)

    if not username or not password:
        return jsonify({'error': 'Please provide a username and password'})

    query = ("SELECT * FROM users2 WHERE username=%s")

    cursor.execute(query, (username,))

    user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'User not found'})

    if not password:
        return jsonify({'error': 'Incorrect password'})

    cursor.close()
    conn.close()

    return jsonify({'username': username, 'password': password_hash})


@app.route('/chat', methods=['POST'])
def chat():
    # Get the database cursor
    cursor = conn.cursor()

    # Get the request data
    data = request.json

    # Get the current time
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Call OpenAI API
    response = openai.Completion.create(
        engine=data['model'],
        prompt=data['prompt'],
        max_tokens=data.get('max_tokens', 256),
        temperature=data.get('temperature', 0.5),
        top_p=data.get('top_p', 1),
        frequency_penalty=data.get('frequency_penalty', 0),
        presence_penalty=data.get('presence_penalty', 0)
    )

    # Prepare the response data
    result = {
        "id": response["id"],
        "object": response["object"],
        "created": response["created"],
        "model": response["model"],
        "choices": response["choices"],
        "usage": {
            "prompt_tokens": response.get("prompt", {}).get("length", 0),
            "completion_tokens": len(response["choices"][0]["text"].split()),
            "total_tokens": response.get("prompt", {}).get("length", 0) + len(response["choices"][0]["text"].split())
        }
    }

    # Print the response text for debugging
    for choice in response["choices"]:
        print(choice["text"])
        str = choice["text"]


    # Insert the request data and response status into the database
    query = "INSERT INTO chat2(model, prompt, max_token, temperature, top_p, frequency_penalty, presence_penalty, request_date, result_tag,result) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)"
    values = (data['model'], data['prompt'], data.get('max_tokens', 256), data.get('temperature', 0.5), data.get('top_p', 1), data.get('frequency_penalty', 0), data.get('presence_penalty', 0), current_time, "Success",str)
    cursor.execute(query, values)
    conn.commit()

    # Close the database cursor
    cursor.close()

    # Return the response data as JSON
    return jsonify(result)



if __name__ == '__main__':

    app.run(debug=True,port=8080)




