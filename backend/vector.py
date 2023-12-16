from flask import Flask, redirect, url_for, request, jsonify, make_response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt import JWT, jwt_required,current_identity

import jwt as pyjwt # Use a different name for PyJWT

import os
from werkzeug.utils import secure_filename
import cv2
from functools import wraps
import numpy as np
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

base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
            data = pyjwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = db.admin.find_one({'username': data["identity"]})
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401        
        return f(user, *args, **kwargs)
    return decorated

def process_image(file_path):
    img = kimage.load_img(file_path, target_size=(224, 224))
    img_array = kimage.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

def get_image_vector(file_path):
    print(file_path)
    img_array = process_image(file_path)
    print(img_array)

    vector = base_model.predict(img_array)
    vector = vector.flatten()
    return vector

@app.route('/admin/create_user', methods=["POST"])
@token_required
def create_user(current_identity):
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
    # image_path = os.path.join(app.config["UPLOAD_FOLDER"],f'uploads/{filename}')
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(image_path)

    # Get image vector from the uploaded image
    image_vector = get_image_vector(image_path)

    # Insert user into the database with the image path
    
    # db.users.insert_one({'username': username, 'image_path': image_path})
    db.users.insert_one({'username': username, 'image_path': image_path, 'image_vector': image_vector.tolist()})

    return jsonify({"message": "User created successfully"}), 201

@app.route('/admin/verify_user', methods=["POST"])
@token_required
def verify_user(current_identity):
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

    # Check if the username exists in the database
    existing_user = db.users.find_one({'username': username})
    if not existing_user:
        return jsonify({"message": "User not found"}), 404
    
    # Save img in a local folder named "uploads"
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"],filename)
    image.save(image_path)

    # Get image vector from the uploaded image
    uploaded_imaged_vector = get_image_vector(image_path)

    # Compare the uploaded image vector with the stored user image vector
    stored_image_vector = np.array(existing_user.get('image',[]))
    if not np.array_equal(uploaded_imaged_vector, stored_image_vector):
        return jsonify({"message":"Image verification failed"}),401

    return jsonify({"message": "User verification successfully"}), 200


@app.route('/admin/get_all_user',methods=["GET"])
@token_required
def get_all_user(current_identity):
    print(current_identity)
    
    # Retrieve all the users from the database
    users = db.users.find({},{'_id': 0, 'username': 1, 'image_path': 1})

    users_list= list(users)

    return jsonify({"user": users_list})

if __name__ == "__main__":
    app.run(debug=True,port=5000)
