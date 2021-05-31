import os

from flask import Flask, render_template, request, redirect

import pandas as pd 
import numpy as np
from sklearn.svm import SVC
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml
import pickle

app = Flask(__name__)

app = Flask(__name__) 
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/login',methods=['POST'])
def login():
    
    username = request.form['username']
    password = request.form['password']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * from user where binary username=%s and binary password=%s",[username,password])
    if(result>0):
        return render_template("index.html", username=username)
    else:
        error = 'failed'
        return render_template("login.html", error=error)


@app.route('/predict', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        cough = request.form['cough']
        fever = request.form['fever']
        throat = request.form['throat']
        breath = request.form['breath']
        data = [cough,fever,throat,breath]
        data = np.array(data)
        data = data.reshape(1, -1)
        model = pickle.load(open('covid_model.pkl','rb'))
        prediction = model.predict(data)
        if prediction == 1:
            result = 'you have been tested possitive for covid-19, please see a doctor'
        elif prediction == 0:
             result = 'you have been tested negative for covid-19, please stay safe'
        else:
            result = 'no data found'
        name = 'Innocent'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO result(username,result) VALUES(%s, %s)", (name,result))
        mysql.connection.commit()
        cur.close()
        return render_template('index.html',
                               class_name=result)
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template("admin.html")


      
@app.route('/admin_login',methods=['POST'])
def admin_login():
    
    
        
    user = request.form['username']
    pass1 = request.form['password']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * from doctor where binary username=%s and binary password=%s",[user,pass1])
    if(result>0):
         cur = mysql.connection.cursor()
         result1 = cur.execute("SELECT * from result")
         if(result1>0):
        
             result3 = cur.fetchall()
        
         return render_template("admin_login.html", result2=result3)
    
    else:
    
        error = 'failed'
        return render_template("admin.html", error=error)
   
        
    

if __name__ == '__main__':
    app.run(debug=True)
