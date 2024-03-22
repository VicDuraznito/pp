





from werkzeug.security import check_password_hash #, generate_password_hash
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, id, username, password, role="") -> None:
        self.id = id
        self.username = username
        self.password = password
        self.role = role

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)


password = 'scrypt:32768:8:1$fvfmx0UUnRuoklPs$d60ce4a63258123dec56274f763eb1139f4d3a718a36c5e18b9128fdb309ec6cdff18fd646e8b0de800f84c422605804200288af9a3a1c133272160217fa3c2c' 

#print(generate_password_hash("admin"))