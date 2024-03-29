from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from werkzeug.utils import secure_filename
import os



app = Flask(__name__)
app.secret_key = 'your_secret_key' # Replace 'your_secret_key' with a secret key for your application


# Load or create the JSON database
try:
    with open('users.json', 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

with open('users.json', 'w') as f:
    json.dump(users, f)


try:
    with open('blog.json', 'r') as f:
        blog = json.load(f)
except FileNotFoundError:
    blog = {}

with open('blog.json', 'w') as f:
    json.dump(blog, f)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username # Store the username in the session
            return redirect(url_for('main', username=username)) # Corrected here
        else:
            return "Invalid username or password", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = {'password': password, 'chathistory': []}
            with open('users.json', 'w') as f:
                json.dump(users, f)
            return redirect(url_for('login'))
        else:
            return "Username already exists", 400
    return render_template('register.html')
@app.route('/profile/<username>')
def main(username):
    username = username # This should be dynamically determined
    return render_template('main.html', username=username)

@app.route('/userpage/<username>')
def userpage(username):
    print(f"Displaying userpage for {username}")
    if username in users:
        return render_template('userpage.html', username=username, chathistory=users[username]['chathistory'])
    else:
        return "User not found", 404

 
  
# New route for viewing a user's profile

# New route for AI chat
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    username = session.get('username', 'default_user')
    if request.method == 'POST':
        message = request.form['message']
        output = query({"inputs": message})
        ai_response = output[0] if output else 'AI response not available'

        if username not in users:
            users[username] = {'chathistory': []}
        users[username]['chathistory'].append({'type': 'user', 'text': message})
        users[username]['chathistory'].append({'type': 'ai', 'text': ai_response})
        with open('users.json', 'w') as f:
            json.dump(users, f)
        return redirect(url_for('chat'))
    if username in users:
        messages = users[username]['chathistory']
    return render_template('chat.html', messages=messages)

@app.route('/admin', methods=['GET', 'POST'])
def print_json_db():
    if request.method == 'POST':
        admin_id = 'admin'
        admin_password = 'password'
        provided_id = request.form.get('id')
        provided_password = request.form.get('password')

        if provided_id == admin_id and provided_password == admin_password:
            return redirect(url_for('table'))
        else:
            return "Invalid ID or password", 401
    return render_template('admin.html')
@app.route('/upload_blog/<username>', methods=['GET', 'POST'])
def upload_blog(username):
    if request.method == 'POST':
        # Handle the form submission here
        text = request.form['text']
        image = request.files['image']
        comment = request.form['comment']
        rating = request.form.get('rating') # Assuming rating is optional

        # Save the text and image to your database or file system
        # For example, saving the image to a directory
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image_path = os.path.join('uploads', image_filename)
            image.save(image_path)
          

        # Process the comment and rating as needed
        # For example, save them to a database

        # Redirect to a success page or back to the form
            
        if username not in blog:
                blog[username] = {'text': text, 'image':image_path ,'comment':comment,'rating':rating}
                with open('blog.json', 'w') as f:
                   json.dump(blog, f)

    return render_template('upload_blog.html')
@app.route('/upload_blog_success')
def upload_blog_success():
    return render_template('upload_blog_success.html')



@app.route('/table', methods=['GET', 'POST'])
def table():
    return render_template('table.html')

# New route for the front page
#@app.route('/front_page')
#def front_page():
 #   return render_template('front_page.html')

if __name__ == '__main__':
    app.run(debug=True)
