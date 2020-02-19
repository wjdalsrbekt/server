#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import werkzeug
import time
import flask
from flask import Flask,request, render_template,redirect, session,jsonify
from flask_sqlalchemy import SQLAlchemy
import instagram
from fastai.vision import *
import pickle
import os

app=Flask(__name__)
app.config['SECRET_KEY'] = 'doctor plant'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['image_save']='./images'
db = SQLAlchemy(app)

class User(db.Model):
    """ Create user table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    predict_img = db.Column(db.String(100), default='default.png')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/login', methods=['GET', 'POST'])
def home():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('log.html')
	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('log.html', data=getfollowedby(username))
		return render_template('log.html')


@app.route('/loginpage', methods=['GET', 'POST'])
def login():
	"""Login Form"""
	if request.method == 'GET':
		return render_template('login.html')
	else:
		name = request.form['username']
		passw = request.form['password']
		try:
			data = User.query.filter_by(username=name, password=passw).first()
			if data is not None:
				session['logged_in'] = True
				return redirect(url_for('home'))
			else:
				return 'Dont Login'
		except:
			return "Dont Login"

@app.route('/register/', methods=['GET', 'POST'])
def register():
	"""Register Form"""
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
	return render_template('register.html')

@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))

@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html')

@app.route('/predict', methods=['POST'])
def upload_file():
    if request.method=='POST':
        file=request.files['image']
        file.save(os.path.join(app.config['image_save'],file.filename))
        if not file:return render_template('index.html', ml_label="No Files")
        temp=open_image(file)
        prediction=model.predict(temp)
        return flask.render_template('index.html', ml_label=prediction[0])

@app.route('/download', methods=['POST'])
def downlaod_file():
    if request.method=='POST':
        file=request.files['image']
        file.save(os.path.join(app.config['image_save'],file.filename))
        temp=open_image(file)
        prediction=model.predict(temp) 
        final={prediction:str(prediction[0])}
    return jsonify(final)

@app.route('/android', methods = ['GET', 'POST'])
def handle_request():
    files_ids = list(flask.request.files)
    for file_id in files_ids:
        imagefile = flask.request.files[file_id]
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        timestr = time.strftime("%Y%m%d")
        imagefile.save(os.path.join(app.config['image_save'],timestr+'_'+filename))
    for filename in os.listdir("."):
        if filename.endswith("jpg"):
           new_filename = filename.replace(timestr+'_'+filename,"1")
           os.rename(filename, new_filename)
    return "Successfully"


if __name__=='__main__':
    app.debug=False
   # db.create_all()
    app.secret_key="123"
    model=load_learner('./','export.pkl')
    app.run(host='0.0.0.0', port=3389, debug=False)


# In[ ]:




