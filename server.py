# from flask import Flask, render_template, request, redirect, url_for
# from flask_pymongo import PyMongo
# from models import User
# from pymongo import MongoClient

# app = Flask(__name__)

# client = MongoClient('mongodb://localhost:27017/')
# db = client['iot']
# users_collection = db['users']

# @app.route('/')
# def home():
#     return 'Home Page'

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         image_url = request.form['image_url']

#         # Save user data to MongoDB
#         user_data = {
#             'username': username,
#             'image_url': image_url
#         }
#         users_collection.insert_one(user_data)

#         return 'User registered successfully'

#     return render_template('register.html')

# if __name__ == '__main__':
#     app.run(debug=True,port=5000)
