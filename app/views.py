from app import app,db,lm
from models import *
from forms import *
from flask import url_for , render_template, request, redirect,g, json
from flask.ext.login import login_user, logout_user, current_user, login_required
import poplib
from email import parser
from sqlalchemy import or_, and_
from werkzeug import secure_filename
import os
import pprint
from imgurpython import ImgurClient

client_id = 'c949fed7ef832fb'
client_secret = '2a429d5633beab712b3c4b5a0e632fccdc516a60'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/user', methods=["GET","POST"])
def user():
#    return 'Hello duniya'
    if request.method == 'GET':
        user = User.query.get(request.args.get('userid'))
        return json.dumps(dict(userid = user.id, name = user.name, profile_url = user.profile_url))
    else:
        user = User(name = request.args.get('name'), profile_url = request.args.get('profile_url'),
                    fb_userid = request.args.get('userid'))
    	#print 'Printing user',user
        db.session.add(user)
        # login_user(user)
       # return redirect(url_for('index'))
    	db.session.commit()
    	userid = User.query.filter_by(name=user.name).first().id
    	return json.dumps(dict(userid = user.id))
	
@app.route('/trip', methods=["GET","POST","PUT"])
def trip():
    if request.method == 'GET':
        trip = TripsMaster.query.get(request.args.get('tripid'))
        map_info = dict()
    	map_info['start_location'] = str(trip.start_location)
    	map_info['end_location'] = str(trip.end_location)
    	map_info['rating'] = str(trip.rating)
    	map_info['vehicle'] = str(trip.vehicle)
    	map_info['start_timestamp'] = str(trip.start_timestamp)
    	map_info['end_timestamp'] = str(trip.end_timestamp)
    	map_info['map_markers'] = []
    	for x in TripDetails.query.filter_by(tripsmaster=TripsMaster.query.get(tripid)):
            map_info['map_markers'].append(dict(location=x.location, text=x.text, image=x.image))
    	print json.dumps(map_info)
        return json.dumps(map_info)
		
    elif request.method == 'POST':
        u = User.query.get(request.args.get('userid'))
        tripsmaster = TripsMaster(user=u,trip_type=request.args.get('trip_type'),
                                  trip_friends=request.args.get('trip_type'),
                                  vehicle=request.args.get('vehicle'),
                                  start_location = request.args.get('start_location'),
                                  start_timestamp = request.args.get('start_timestamp'))
        db.session.add(tripsmaster)
        db.session.commit()
        tripid= tripsmaster.query.filter_by(user=u).first().id
        return json.dumps(dict(tripid = tripid))
    else:
        trip = TripsMaster.query.get(request.args.get('tripid'))
        trip.end_timestamp=request.args.get('end_timestamp')
        trip.privacy = request.args.get('privacy')
        trip.rating = request.args.get('rating')
        trip.end_location = request.args.get('end_location')
        db.session.commit()
        map_info = dict()
        trip = TripsMaster.query.get(request.args.get('tripid'))
        map_info['start_location'] = str(trip.start_location)
        map_info['end_location'] = str(trip.end_location)
        map_info['rating'] = str(trip.rating)
        map_info['vehicle'] = str(trip.vehicle)
        map_info['start_timestamp'] = str(trip.start_timestamp)
        map_info['end_timestamp'] = str(trip.end_timestamp)
        map_info['map_markers'] = []
        for x in TripDetails.query.filter_by(tripsmaster=TripsMaster.query.get(tripid)):
            map_info['map_markers'].append(dict(location=x.location, text=x.text, image=x.image))
        return json.dumps(map_info)

@app.route('/trips', methods=["GET"])
def trips():
    if request.method == 'GET':
        trips=[]
        for x in TripsMaster.query.filter_by(user = User.query.get(request.args.get('userid'))):
            trips.append(x)	
        trip_list=[]
        for trip in trips:
            map_info={}			
            map_info['start_location'] = str(trip.start_location)
            map_info['end_location'] = str(trip.end_location)
            map_info['rating'] = str(trip.rating)
            map_info['vehicle'] = str(trip.vehicle)
            map_info['start_timestamp'] = str(trip.start_timestamp)
            map_info['end_timestamp'] = str(trip.end_timestamp)
            map_info['map_markers'] = []
            for x in TripDetails.query.filter_by(tripsmaster=TripsMaster.query.get(tripid)):
                map_info['map_markers'].append(dict(location=x.location, text=x.text, image=x.image))
            trip_list.append(map_info)
            return json.dumps(trip_list)

@app.route('/pitstop', methods=["GET", "POST"])
def pitstop(tripid, userid):
    if request.method == 'GET':
        tripdetails=[]
        for x in TripDetails.query.filter_by(tripsmaster=request.args.get('tripid')):
            tripdetails.append(dict(location=x.location, text=x.text, image=x.image))
        return json.dumps(tripdetails)
    else:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        client = ImgurClient(client_id, client_secret)
        response = client.upload_from_path('/home/chakshu/WanderLust/Uploads/'+filename)
        tpid = TripsMaster.query.get(request.args.get('tripid'))
        tripdetails = TripDetails(tripsmaster = tpid,location=request.args.get('location'),
                                  timestamp=request.args.get('timestamp'),
                                  text=request.args.get('text'),
                                  image = str(response['link']))
        db.session.add(tripdetails)
       	# login_user(user)
       	# return redirect(url_for('index'))
        db.session.commit()
        tripdetails=[]
        for x in TripDetails.query.filter_by(tripsmaster=request.args.get('tripid')):
            tripdetails.append(dict(location=x.location, text=x.text, image=x.image))
        return json.dumps(tripdetails)

@app.route('/chatbot/<threadID>/', methods=["GET"])
def chatbot(threadID):
    print 'Did I enter'
    msg = request.args.get('msg')
    print msg
    places = msg.split('#')[1:]
    print places
    start_end = []
    for place in places:
	place = str(place)
        start_end.append(place.split(' ')[0])
    start = start_end[0]
    end = start_end[1]
    print start, end
    map_info = dict()
    trip = TripsMaster.query.filter_by(start_location=start, end_location=end).first()
    map_info['start_location'] = str(trip.start_location)
    map_info['end_location'] = str(trip.end_location)
    map_info['rating'] = str(trip.rating)
    map_info['vehicle'] = str(trip.vehicle)
    map_info['start_timestamp'] = str(trip.start_timestamp)
    map_info['end_timestamp'] = str(trip.end_timestamp)
    map_info['map_markers'] = []
    response = 'Oh, looking for trip from '+map_info['start_location']+' to '+map_info['end_location'] + ' ? ' + ' You remember you took stop overs at '
    for x in TripDetails.query.filter_by(tripsmaster=TripsMaster.query.get(trip.id)):
       	map_info['map_markers'].append(dict(location=x.location, text=x.text, image=x.image))
        response += x.location + ' with this view as ' + x.image + 'and comments as ' + x.text
  		
    #return json.dumps(map_info)
    return response

@app.route('/search', methods=["GET"])
def search():
    if request.method == 'GET':
        start = request.args.get('From')
        end = request.args.get('To')
        search_info = dict()
    	search_info['search_results'] = []
        if start != '' and end != '':
            for x in TripsMaster.query.filter_by(start_location=start).filter_by(end_location=end):
                s_dict = dict(start_location=x.start_location, end_location=x.end_location, userid = x.userid)                
                s_dict['map_markers'] = []
                for y in TripDetails.query.filter_by(tripsmaster=TripsMaster.query.get(x.id)):
                    s_dict['map_markers'].append(dict(location=y.location, text=y.text, image=y.image))
                search_info['search_results'].append(s_dict)
        elif start != '':
            for x in TripsMaster.query.filter_by(start_location=start):
                s_dict = dict(start_location=x.start_location, end_location=x.end_location, userid = x.userid)
                search_info['search_results'].append(s_dict)
    	elif end != '':
            for x in TripsMaster.query.filter_by(end_location=end):
                s_dict = dict(start_location=x.start_location, end_location=x.end_location, userid = x.userid)
                search_info['search_results'].append(s_dict)
	    print json.dumps(search_info)
            return json.dumps(search_info)

