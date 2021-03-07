# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 18:39:31 2021

@author: Onkar
"""

from flask import Flask, render_template, request, Response,session
import mysql.connector
import xlrd
import cv2
import numpy as np
import face_recognition
import os

app = Flask(__name__)
app.config["UPLOADS"] = "C:/Users/Oggy"
mydb = mysql.connector.connect(
                host = "localhost",
                user = "minaxi",
                password = "minaxi1234",
                database="new_data"
            ) 
app.secret_key = 'Minaxi'     
mycursor = mydb.cursor()
class req:
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/teacher_signup.html')
    def teachersignup():
        return render_template('teacher_signup.html')
    
    @app.route('/student_signup.html')
    def studentsignup():
        return render_template('student_signup.html')
    
    @app.route('/admin_login.html')
    def adminlogin():
        return render_template('admin_login.html')
    
    @app.route('/admin.html')
    def admin():
        return render_template('admin.html')
    
    @app.route('/studentform',methods = ['POST','GET'])
    def studentform():
        msg=''
        if request.method == 'POST':
            mycursor = mydb.cursor()
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            pr_no = request.form['pr']
            roll_no = request.form['rollno']
            course = request.form['Course']
            email = request.form['email']
            password = request.form['password']
            studimg = request.files['img']
            studimg.save(os.path.join(app.config["UPLOADS"], studimg.filename))
            imgname = studimg.filename;
            imgpath = "C:/Users/Oggy/{0}".format(str(imgname))
            with open(imgpath, "rb") as File:
                BinaryData = File.read()
            #check if student already exists or not
            sql1 = "SELECT * FROM student1 WHERE fname = %s AND lname = %s"
            val1 = (first_name, last_name)
            mycursor.execute(sql1,val1)
            account = mycursor.fetchone()
            if account:
                msg = 'Account already exists !'
            else:
                #check if its a official/legit student
                sql2 = "SELECT * FROM studentreg WHERE prno = %s"
                val2 = (pr_no,)
                mycursor.execute(sql2,val2)
                account2 = mycursor.fetchone()
                if account2:
                    mycursor.execute('INSERT INTO student1(prno,fname,lname,rollno,course,email,password,image) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',(pr_no,first_name,last_name,roll_no,course,email,password,BinaryData))
                    mydb.commit()
                    msg = 'You have successfully registered!'
                else:
                    msg = 'Please contact system admin'
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        mycursor.close()
        mydb.commit()
        
        return render_template('student_signup.html',msg=msg)
    
    @app.route('/register_teacher',methods = ['POST','GET'])
    def register_teacher():
        msg = '' 
        if request.method == 'POST': 
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            tid = request.form['tid']
            password = request.form['password'] 
            email = request.form['email'] 
            SQLStatement2 = "SELECT * FROM teacher WHERE fname = %s"
            val = (first_name,)
            mycursor = mydb.cursor()
            mycursor.execute(SQLStatement2,val)
            account = mycursor.fetchone() 
            
            if account: 
                msg = 'Account already exists !'
            else: 
                SQLStatement3 = "SELECT * FROM teacherreg WHERE id = %s"
                val = (tid,)
                mycursor.execute(SQLStatement3,val)
                account1 = mycursor.fetchone()
                if account1:
                    mycursor.execute('INSERT INTO teacher (id,fname,lname,email,password) VALUES (%s,%s,%s,%s,%s)',(tid,first_name,last_name,email,password)) 
                    mydb.commit() 
                    msg = 'You have successfully registered !'
                    mycursor.close()
                else:
                    msg='Please contact system admin'
        elif request.method == 'POST': 
            msg = 'Please fill out the form !'
        return render_template('teacher_signup.html', msg = msg) 
    
    @app.route('/login', methods =['GET', 'POST']) 
    def login(): 
        mycursor=mydb.cursor()
        msg = '' 
        if request.method == 'POST': 
            email = request.form['email'] 
            password = request.form['password'] 
            mycursor.execute('SELECT * FROM teacher WHERE email = %s AND password = %s', (email, password, )) 
            account = mycursor.fetchone() 
            if account:
                session['loggedin'] = True
                session['id'] = account[5] 
                session['username'] = account[0] 
                msg = 'Logged in successfully !'
                return render_template('ui.html', msg = msg) 
            else:
                mycursor.execute('SELECT * FROM student1 WHERE email = %s AND password = %s', (email, password, )) 
                account2 = mycursor.fetchone()
                if account2:
                    session['loggedin'] = True
                    session['id'] = account2[0] 
                    session['username'] = account2[1] 
                    msg = 'Logged in successfully !'
                    return render_template('ui.html', msg = msg)
                else:
                    msg = 'Incorrect username / password !'
        return render_template('index.html', msg = msg) 
  
    @app.route('/logout',methods =['GET', 'POST']) 
    def logout(): 
        session.pop('loggedin', None) 
        session.pop('id', None) 
        session.pop('username', None) 
        #return redirect(url_for('login')) 
        msg='logged out'
        return render_template('index.html',msg=msg) 
    
    @app.route('/admin_login', methods =['GET', 'POST']) 
    def admin_login(): 
        mycursor=mydb.cursor()
        msg = '' 
        if request.method == 'POST': 
            email = request.form['email'] 
            password = request.form['password'] 
            if (email=='minu@g.com' and password=='Minaxi'):
                session['loggedin'] = True
                session['id'] = '123' 
                session['username'] = 'Admin'
                msg = 'Logged in successfully !'
                return render_template('admin.html', msg = msg) 
            else:
                msg = 'Incorrect username / password !'
        return render_template('admin_login.html', msg = msg)
        







    @app.route('/uploadcsv',methods = ['POST','GET'])
    def uploadcsv():
        if request.method == 'POST':
            mycursor = mydb.cursor()
            typefile = request.form['semester']
            file = request.files['myfile']
            file.save(os.path.join(app.config["UPLOADS"], file.filename))
            csvname = file.filename
            xlrd.xlsx.ensure_elementtree_imported(False, None)
            xlrd.xlsx.Element_has_iter = True
            book = xlrd.open_workbook("C:/Users/Oggy/{0}".format(str(csvname)))
            sheet = book.sheet_by_name("Sheet1")
            if typefile == 'Student':
                query = """INSERT INTO studentreg(prno,sname,slast) VALUES (%s, %s, %s)"""
                for r in range(1, sheet.nrows):
                    pr = sheet.cell(r,0).value
                    fn = sheet.cell(r,1).value
                    ln = sheet.cell(r,2).value
                    values = (pr,fn,ln)
                    mycursor.execute(query, values)
            elif typefile == 'Teacher':
                query = """INSERT INTO teacherreg(id,fname,lname) VALUES (%s, %s, %s)"""
                for r in range(1, sheet.nrows):
                    pr = sheet.cell(r,0).value
                    fn = sheet.cell(r,1).value
                    ln = sheet.cell(r,2).value
                    values = (pr,fn,ln)
                    mycursor.execute(query, values)
            mycursor.close()
            mydb.commit()
            
            return render_template("admin.html", msg="File Upload Successful!")
    
    @app.route('/addrec',methods = ['POST','GET'])
    def addrec():
        if request.method == 'POST':

            mycursor = mydb.cursor()

            def RetreiveImages():
                SQLStatement2 = "SELECT username,image from student"
                mycursor.execute(SQLStatement2)
                myresult = mycursor.fetchall()
                for row in myresult:
                    name = row[0]
                    photo = row[1]
                    storefilepath = "C:/Users/Oggy/.spyder-py3/face_recog/image/{0}.jpg".format(str(name))
                    write_file(photo,storefilepath)
        
            def write_file(data, filepath):
                with open(filepath, "wb") as File:
                    File.write(data)
                File.close()
        

            RetreiveImages()

            path = 'C:/Users/Oggy/.spyder-py3/face_recog/image'
            imgList = []
            personNames = []
            myList = os.listdir(path)
            print(myList)
            for cls in myList:
                curImg = cv2.imread(f'{path}/{cls}')
                imgList.append(curImg)
                personNames.append(os.path.splitext(cls)[0])

            def findEncodings(imgList):
                encodeList = []
                for img in imgList:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    encode = face_recognition.face_encodings(img)[0]
                    encodeList.append(encode)
                return encodeList

            encodeListStoredImages = findEncodings(imgList)
            cap = cv2.VideoCapture(0)
            studentsPresent = []

            while True:
                success, img = cap.read()
                imgwebcam = cv2.resize(img,(0,0),None,0.25,0.25)
                imgwebcam = cv2.cvtColor(imgwebcam, cv2.COLOR_BGR2RGB)
                facesInCurrFrame = face_recognition.face_locations(imgwebcam)
                encodeCurrFrame = face_recognition.face_encodings(imgwebcam,facesInCurrFrame)
    
                for encodeFace,faceLoc in zip(encodeCurrFrame,facesInCurrFrame):
                    matches = face_recognition.compare_faces(encodeListStoredImages, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListStoredImages, encodeFace)
                    matchIndex = np.argmin(faceDis)
        
                    if matches[matchIndex]:
                        name = personNames[matchIndex].upper()
                        if name not in studentsPresent:
                            studentsPresent.append(name)
                            SQLStatement2 = "UPDATE attendance SET attend=%s WHERE name=%s"
                            val = ("P",name)
                            mycursor.execute(SQLStatement2,val)
                            mydb.commit()
                        y1,x2,y2,x1 = faceLoc
                        y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                        cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                        cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            
                cv2.imshow('Webcam',img)
                #cv2.waitKey(1)
                if cv2.waitKey(20) & 0xFF == ord('q'):
                    break;
            cap.release()
            cv2.destroyAllWindows()
            return render_template('list_of_student.html', studentsPresent=studentsPresent)
if __name__ == '__main__':
    app.run(debug = True)
obj=req()