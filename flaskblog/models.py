from flaskblog import loginManager, db
from flask_login import UserMixin

@loginManager.user_loader
def loadUser(userId):
    return User.query.get(int(userId))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    imageFile = db.Column(db.String(20), nullable=False, default='lonePine.png')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return ("User('{0}', '{1}', '{2}'".format(self.username, self.email, self.imageFile))


class Place(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    address = db.Column(db.String(100),nullable=True)
    city = db.Column(db.String(100),nullable=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    source = db.Column(db.String(100),nullable=True)

    def __repr__(self):
        return ("{0},{1},{2},{3},{4},{5}".format(self.name, self.address, self.city, self.latitude, self.longitude, self.source))

    def toString(self):
        return ("{0},{1},{2},{3},{4},{5}".format(self.name, self.address, self.city, self.latitude, self.longitude, self.source))
   