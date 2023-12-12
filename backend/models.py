# from flask_pymongo import PyMongo
# from flask_login import UserMixin

# class User(UserMixin):
#     def __init__(self, username, image_url):
#         self.username = username
#         self.image_url = image_url

#     @staticmethod
#     def from_dict(user_dict):
#         return User(
#             username=user_dict.get('username'),
#             image_url=user_dict.get('image_url')
#         )

#     def to_dict(self):
#         return {
#             'username': self.username,
#             'image_url': self.image_url
#         }