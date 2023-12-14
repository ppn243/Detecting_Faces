from flask import Flask, redirect, url_for, request, jsonify, make_response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt import JWT, jwt_required,current_identity

import jwt as pyjwt # Use a different name for PyJWT

import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from functools import wraps
from PIL import PixarImagePlugin

from keras.applications import MobileNetV2
from keras.applications.mobilenet_v2 import preprocess_input
from keras.preprocessing import image as kimage

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://localhost:27017/iot"
app.config['SECRET_KEY'] = 'fc8003bf7e42fbfb602c0e14eacd801ba3a11a75'
app.config['UPLOAD_FOLDER'] = 'uploads' # Folder to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Database
mongodb_client = PyMongo(app)
db = mongodb_client.db
bcrypt = Bcrypt(app)

# Load pre-trained MobileNetV2 model
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to process image and convert it to vector
def process_image(file_path):
    # Load and preprocess the image
    img = kimage.load_img(file_path, target_size=(224, 224))
    img_array = kimage.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    
    return img_array

def get_image_vector(file_path):
    print(file_path)
    img_array = process_image(file_path)
    print(img_array)

    # Get the feature vector from the pre-trained model
    vector = base_model.predict(img_array)
    # Flatten the vector
    vector = vector.flatten()
    return vector

# Admin model
class Admin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
    def jwt_identity(self):
        return self.username

# JWT configuration
def authenticate(username, password):
    user = db.admin.find_one({'username': username})
    if user and bcrypt.check_password_hash(user['password'], password):
        return Admin(username=user['username'], password=user['password'])

def identity(payload):
    user_id = payload['identity']
    return db.admin.find_one({'username': user_id})

# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        user = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            print(token)
            print(app.config['SECRET_KEY'])
            # data = pyjwt.decode(token, app.config['SECRET_KEY'])
            data = pyjwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = db.admin.find_one({'username': data["identity"]})
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        
        print(user)
        return f(user, *args, **kwargs)
    return decorated

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.admin.find_one({'username': username})

    if user and bcrypt.check_password_hash(user['password'], password):
        # Generate JWT token using Flask-JWT
        payload = Admin(username=user['username'], password=user['password']).jwt_identity()
        print(payload)
        token = pyjwt.encode({'identity': payload}, app.config['SECRET_KEY'])

        # Set a cookie for the token
        response = jsonify({'token': token})
        return response
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/admin/logout', methods=['GET'])
def admin_logout():
    # Clear the token cookie by setting an expired cookie
    response = jsonify({'message': 'Logout successful'})
    response.set_cookie('access_token', expires=0, httponly=True, secure=True)  # Expire the cookie
    return response

# Route for admin registration
@app.route('/admin/register', methods=['POST'])
def admin_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if username already exists
    if db.admin.find_one({'username': username}):
        return jsonify({'message': 'Username already exists'}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert user into the database
    db.admin.insert_one({'username': username, 'password': hashed_password})

    return jsonify({'message': 'Registration successful'}), 201

@app.route('/admin/create_user', methods=["POST"])
@token_required
def create_user(current_identity):
    # if current_identity is None or current_identity.username != 'admin':
    #     return jsonify({"message":"Unauthorized access"}), 403
    print(current_identity)

    if 'image' not in request.files or not request.files['image'].filename:
        return jsonify({"message": "No file part"}), 400

    image = request.files["image"]

    if not allowed_file(image.filename):
        return jsonify({"message": "Invalid file extension"}),400

    # Get data from the request (username and multiple image files)
    username = request.form.get('username')
    if not username:
        return jsonify({"message":"UserName is required"}),400

    # Check if username already exists
    existing_user = db.users.find_one({'username': username})
    if existing_user:
        return jsonify({"message":"Username already exits"}), 400
    
    # Save img in a local folder named "uploads"
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"],filename)
    
    image.save(image_path)

    image_vector = get_image_vector(image_path)

    # Insert user into the database with the image path
    db.users.insert_one({'username': username, 'image_path': image_path})

    return jsonify({"message": "User created successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True,port=5000)
