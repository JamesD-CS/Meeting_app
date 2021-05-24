from flask import Flask, render_template, json, request, redirect, Response, jsonify, session, g
import os 
import sqlite3
import pytz
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from datetimerange import DateTimeRange
import requests
# Configuration

app = Flask(__name__)
# set SQLALCHEMY_TRACK_MODIFICATIONS to False to prevent deprecation warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meetings.sqlite3'
db = SQLAlchemy(app)

# Meeting class definition for sqlalchemy
class Meeting(db.Model):
	__tablename__ = 'meetings'
	__table_args__ = { 'extend_existing': True }
	id = db.Column(db.Integer, primary_key=True)  
	name = db.Column(db.String)
	start_time = db.Column(db.String)
	end_time = db.Column(db.String)
	time_zone = db.Column(db.String)
	offset = db.Column(db.String)
	is_minus = db.Column(db.Integer)
	start_simple = db.Column(db.String)
	end_simple = db.Column(db.String)
# Routes 

# Recursive function for calculating meeting time intersections in a list
def get_intersect(numlist):
    if len(numlist) == 1:
        return numlist[0]
    else:
        return numlist[0].intersection(get_intersect(numlist[1:]))

@app.route('/test')
def test():
	return "Hello World!"

@app.route('/', methods = ['GET'])
def show_main():
	meeting_list = Meeting.query.all()
	dt_list = []
	# convert meeting start and end time to DateTimeRange object to calculate time intersection
	for meetings in meeting_list:
		dt_range=DateTimeRange(meetings.start_time, meetings.end_time)
		dt_list.append(dt_range)
	start_time = "No Time Available"
	end_time = "No Time Available"
	if len(dt_list) > 1:
		calc_time = get_intersect(dt_list)
		
		# Convert time to standard format for local timezone conversion in browser
		calc_time = str(calc_time)
		time_list = calc_time.split(" - ")
		start_time = time_list[0]
		start_time = start_time.replace(':00+0000', ':00Z')
		end_time = time_list[1]
		end_time = end_time.replace(':00+0000', ':00Z')
		#print(start_time)
		if "NaT" in str(calc_time):
			calc_time = "No Meeting Time Available"
	
	return render_template("main.j2", meetings = meeting_list, start_time=start_time, end_time = end_time )

@app.route('/add-meeting', methods = ['POST'])
def add_meeting():
	name = request.form['name']
	time_zone = request.form['tz_name']
	start_time = str(request.form['start_time'])
	end_time = str(request.form['end_time'])
	offset = str(request.form['time_zone'])
	new_meeting = Meeting()
	offset = offset.replace(':', '')
	
	# Convert time to python datetime format. If UTC offset is negative set meeting.is_minus to 1
	
	new_meeting.start_time = datetime.strptime("2021-1-1 "+ start_time + offset, '%Y-%m-%d %H:%M%z') 
	new_meeting.end_time = datetime.strptime("2021-1-1 "+  end_time + offset, '%Y-%m-%d %H:%M%z') 
	
	
	new_meeting.start_time = new_meeting.start_time.astimezone(pytz.utc) 
	new_meeting.end_time = new_meeting.end_time.astimezone(pytz.utc)
	new_meeting.start_time = str(new_meeting.start_time)
	new_meeting.end_time = str(new_meeting.end_time)
	print(new_meeting.start_time)
	print(new_meeting.end_time)
	new_meeting.name = name
	new_meeting.time_zone = time_zone
	new_meeting.start_simple = start_time
	new_meeting.end_simple = end_time
	
	new_meeting.offset = offset
	
	db.session.add(new_meeting)
	db.session.commit()

	return redirect("/")

@app.route('/delete/<int:id>', methods = ['GET'])
def delete_meeting(id):

	Meeting.query.filter_by(id = id).delete()
	db.session.commit()

	return redirect("/")


@app.route('/send-email', methods = ['POST'])
def send_email():
	meeting_time = request.form['meeting_time']
	email = request.form['email']
	url = "http://flip1.engr.oregonstate.edu:9584/"
	json_req = {
  	"recipient": email,
  	"senderName": "Meeting Reminder Service",
  	"senderEmail": "test@email.com",
  	"subject": "Reminder about your scheduled meeting",
  	"text": "Hello, this is a reminder that your shceduled meeting time is at: " + meeting_time,
  	"html": "<!DOCTYPE html><html><body><h1>Reminder about your scheduled meeting</h1><h2>Hello, this is a reminder that your shceduled meeting time is at: "+ meeting_time+"</h2></body></html>"
	}
	requests.post(url, json=json_req)
	return redirect("/")

@app.route('/db-test')
def db_test():
	#meeting = Meeting.query.first()
	#name = meeting.name
	meeting_list = Meeting.query.all()
	return render_template("main.j2", meetings = meeting_list)




# Listener

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 9112)) 
	#                                 ^^^^
	#              You can replace this number with any valid port
	
	app.run(port=port, debug=True) 