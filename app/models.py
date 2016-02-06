from app import db
import datetime

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    profile_url = db.Column(db.String)
    fb_userid = db.Column(db.String)
    trips = db.relationship('TripsMaster', backref='user', lazy='dynamic')

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % (self.id)

class TripsMaster(db.Model):
    __tablename__ = 'tripsmaster'
    id = db.Column(db.Integer , primary_key=True,autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_timestamp = db.Column(db.String,default=datetime.datetime.utcnow)
    end_timestamp = db.Column(db.String,default=datetime.datetime.utcnow)
    start_location = db.Column(db.String)
    end_location = db.Column(db.String)
    rating = db.Column(db.Float)
    privacy = db.Column(db.Boolean)
    trip_type = db.Column(db.String)
    vehicle = db.Column(db.String)
    trip_friends = db.Column(db.String)
    tripdetails = db.relationship('TripDetails', backref='tripsmaster', lazy='dynamic')

'''
    def __init__(self,userid=None,
            start_timestamp=None,
            end_timestamp=None,
            start_location=None,
            end_location=None,
            rating=None,
            privacy=None,
            trip_type=None,
            vehicle=None,
            trip_friends=None):
        self.userid = userid
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.start_location = start_location
        self.end_location = end_location
        self.rating = rating
        self.privacy= privacy
        self.trip_type=trip_type
        self.vehicle=vehicle
        self.trip_friends=trip_friends
'''

class TripDetails(db.Model):
    __tablename__ = 'tripdetails'
    id = db.Column(db.Integer , primary_key=True,autoincrement=True)
    #tmid = #foreign key to TripMaster
    tmid = db.Column(db.Integer, db.ForeignKey('tripsmaster.id'))
    location =db.Column(db.String)
    timestamp = db.Column(db.String,default=datetime.datetime.utcnow)
    text = db.Column(db.String)
    image = db.Column(db.String)
'''
    def __init__(self,tmid=None,location=None,timestamp=None,text=None,image=None):
        self.tmid=tmid
        self.location=location
        self.timestamp=timestamp
        self.text=text
        self.image=image
'''
