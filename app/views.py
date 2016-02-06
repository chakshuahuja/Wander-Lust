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
@app.route('/index')
def index():
#    return 'Hello duniya'
    return render_template('index.html')

@app.route('/tripstarted/<userid>/<tripid>')
def tripstarted(tripid, userid):

    trip = TripsMaster.query.get(tripid)
    return render_template('tripstarted.html',tripid=tripid,userid=userid,trip_start_location=trip.start_location)

@app.route('/dashboard/<userid>', methods=["GET"])
def dashboard(userid):
    if request.method == 'GET':
        trips=[]
        for x in TripsMaster.query.filter_by(user = User.query.get(userid)):
            trips.append(x)	
            places_visited = []
		#print dir(trips)
		#print trips	
            for x in trips:
                places_visited.append(str(x.start_location))
                places_visited.append(str(x.end_location))
		#print places_visited    
        return render_template('dashboard.html',userid = userid)
            
@app.route('/search/<userid>', methods=["GET"])
def search(userid):
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

        return render_template('dashboard.html',userid = userid)

@app.route('/start/<userid>', methods=["GET", "POST"])
def start(userid):
    form = StartTripForm()

    if request.method == 'GET':
        return render_template('start.html',form=form)
    if form.validate_on_submit():
	print form
	u = User.query.get(userid)
	print u
        tripsmaster = TripsMaster(user=u,trip_type=form.trip_type.data,
                trip_friends=form.trip_friends.data,
                vehicle=form.vehicle.data,
                start_location = form.start_location.data,
                start_timestamp = form.start_timestamp.data)
        db.session.add(tripsmaster)
        db.session.commit()
    	tripid= tripsmaster.query.filter_by(start_timestamp=tripsmaster.start_timestamp).first().id

    return redirect(url_for('tripstarted',userid=userid, tripid=tripid))

@app.route('/end/<userid>/<tripid>', methods=["GET", "POST"])
def end(tripid, userid):
    form = EndTripForm()

    if request.method == 'GET':
        return render_template('end.html',form=form)

    if form.validate_on_submit():
        trip = TripsMaster.query.get(tripid)
        trip.end_timestamp=form.end_timestamp.data
        trip.privacy = form.privacy.data
        trip.rating = form.rating.data
        trip.end_location = form.end_location.data
        db.session.commit()
    	map_info = dict()
    	trip = TripsMaster.query.get(tripid)
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

    return redirect(url_for('dashboard',userid=userid))

@app.route('/pitstop/<userid>/<tripid>', methods=["GET", "POST"])
def pitstop(tripid, userid):
    form = PitStopForm()

    if request.method == 'GET':
        return render_template('pitstop.html',form=form,userid=userid,tripid=tripid)

    if form.validate_on_submit():
        file = request.files['image']
        print dir(request)
	if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
           
	    client = ImgurClient(client_id, client_secret)
            response = client.upload_from_path('/home/chakshu/WanderLust/Uploads/'+filename)
            
	    tpid = TripsMaster.query.get(tripid)
            tripdetails = TripDetails(tripsmaster = tpid,location=request.form['location'],
                    timestamp=request.form['timestamp'],
                    text=request.form['text'],
                    image = str(response['link']))
            db.session.add(tripdetails)
       # login_user(user)
       # return redirect(url_for('index'))
            db.session.commit()
	
    return redirect(url_for('tripstarted',tripid=tripid, userid=userid))

@app.route('/profileinfo', methods=["POST"])
def profileinfo():
    user = User(name = request.form['name'], profile_url = request.form['profile_url'],
                    	fb_userid = request.form['id'])
    #print 'Printing user',user
    db.session.add(user)
       # login_user(user)
       # return redirect(url_for('index'))
    db.session.commit()
    userid = User.query.filter_by(name=user.name).first().id
    return redirect(url_for('dashboard', userid = userid))


