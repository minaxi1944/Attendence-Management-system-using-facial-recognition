# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 18:39:31 2021

@author: Onkar
"""

from flask import Flask, render_template, request, Response, session
import mysql.connector
import xlrd
import cv2
import numpy as np
import os
import io
import smtplib
import datetime

app = Flask(__name__)
app.config["UPLOADS"] = "C:/Users/Oggy"
app.secret_key = 'Onkar'

class req:
        
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/register_subject.html')
    def registersubject():
        return render_template('register_subject.html',username=session['username'])
    @app.route('/sendmail1.html')
    def email2():
        return render_template('sendmail1.html', username=session['username'])
    
    @app.route('/student_dashboard.html')
    def student_dashboard():
        msg=''
        mydb = mysql.connector.connect(
               host="localhost",
               user="root",
               password="",
               database="attendance_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT rollno FROM student where prno=%s",(session['id'],))
        roll = mycursor.fetchone()
        mycursor.execute("SELECT subject_name,subject_code FROM student_subject where roll_no=%s",(roll[0],))
        subj = mycursor.fetchall()
        return render_template('student_dashboard.html',username=session['username'],msg=subj)
    
    @app.route('/teacher_dashboard.html')
    def teacher_dashboard():
        msg=''
        mydb = mysql.connector.connect(
               host="localhost",
               user="root",
               password="",
               database="attendance_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT subject_name,subject_code,semester FROM teacher_subject where teacher_id=%s",(session['id'],))
        subj = mycursor.fetchall()
        return render_template('teacher_dashboard.html',username=session['username'],msg=subj)
    
    @app.route('/teacher_email.html')
    def teacheremail():
        return render_template('teacher_email.html',username=session['username'])
    
    @app.route('/teacher_signup.html')
    def teachersignup():
        return render_template('teacher_signup.html')
    
    @app.route('/student_signup.html')
    def studentsignup():
        return render_template('student_signup.html')
    
    @app.route('/student_semester.html')
    def student_semester():
        return render_template('student_semester.html',username=session['username'])
    
    @app.route('/admin_login.html')
    def adminlogin():
        return render_template('admin_login.html')
    
    @app.route('/admin.html')
    def admin():
        return render_template('admin.html')
    
    @app.route('/studentattendance', methods = ['POST', 'GET'])
    def studentattendance():
        msg=''
        if request.method == 'POST':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT prno FROM studentreg")
            rollno = mycursor.fetchall()

        return render_template('attendance_formm.html', msg=rollno)
    
    @app.route('/attendance_form', methods = ['POST', 'GET'])
    def attendance_form():
        msg=''
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_db"
        )
        mycursor = mydb.cursor()
        semester = request.form['semester']
        mycursor.execute("SELECT subject_name FROM teacher_subject where teacher_id=%s and semester=%s",(session['id'],semester,))
        
        
        subjectn = mycursor.fetchall()
        return render_template('attendance_form.html', msg=subjectn)
        
    @app.route('/attendance_sem', methods = ['POST', 'GET'])
    def attendance_sem():
        return render_template('attendance_sem.html',)

    
    @app.route('/studentform',methods = ['POST','GET'])
    def studentform():
        msg=''
        if request.method == 'POST':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            )
            mycursor = mydb.cursor()

            first_name = request.form['firstname']
            last_name = request.form['lastname']
            pr_no = request.form['phone']
            roll_no = request.form['rollno']
            course = request.form['Course']
            email = request.form['email']
            password = request.form['password']
            studimg = request.files['img']
            studimg.save(os.path.join(app.config["UPLOADS"], studimg.filename))
            imgname = studimg.filename;
            imgpath = "C:/Users/Onkar/{0}".format(str(imgname))
            with open(imgpath, "rb") as File:
                BinaryData = File.read()
            #check if student already exists or not
            sql1 = "SELECT * FROM student WHERE fname = %s AND lname = %s"
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
                    mycursor.execute('INSERT INTO student(prno,fname,lname,rollno,course,email,password,image) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',(pr_no,first_name,last_name,roll_no,course,email,password,BinaryData))
                    mydb.commit()
                    msg = 'You have successfully registered!'
                else:
                    msg = 'Please contact system admin'
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        mycursor.close()
        mydb.commit()
        mydb.close()
        return render_template('student_signup.html',msg=msg)
    
    @app.route('/register_teacher',methods = ['POST','GET'])
    def register_teacher():
        msg = '' 
        if request.method == 'POST': 
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            tid = request.form['phone']
            password = request.form['password'] 
            email = request.form['email'] 
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            ) 
           
            mycursor = mydb.cursor()
            SQLStatement2 = "SELECT * FROM teacher WHERE fname = %s"
            val = (first_name,)
            mycursor.execute(SQLStatement2,val)
            account = mycursor.fetchone() 
            
            if account: 
                msg = 'Account already exists !'
            else: 
                SQLStatement3 = "SELECT * FROM teacherreg WHERE trid = %s"
                val = (tid,)
                mycursor.execute(SQLStatement3,val)
                account1 = mycursor.fetchone()
                if account1:
                    mycursor.execute('INSERT INTO teacher (id,fname,lname,email,password) VALUES (%s,%s,%s,%s,%s)',(tid,first_name,last_name,email,password)) 
                    mydb.commit() 
                    msg = 'You have successfully registered !'
                else:
                    msg='Please contact system admin'
        elif request.method == 'POST': 
            msg = 'Please fill out the form !'
        return render_template('teacher_signup.html', msg = msg) 
    
    @app.route('/login', methods =['GET', 'POST']) 
    def login(): 
        mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            ) 
        mycursor = mydb.cursor()
        msg = '' 
        if request.method == 'POST': 
            email = request.form['email'] 
            password = request.form['password'] 
            mycursor.execute('SELECT * FROM teacher WHERE email = %s AND password = %s', (email, password, )) 
            account = mycursor.fetchone() 
            if account:
                session['loggedin'] = True
                session['id'] = account[0] 
                session['username'] = account[1] 
                msg = 'Logged in successfully !'
                mycursor.execute("SELECT subject_name,subject_code,semester FROM teacher_subject where teacher_id=%s",(session['id'],))
                subj = mycursor.fetchall()
                return render_template('teacher_dashboard.html',username=session['username'],msg=subj) 
            else:
                mycursor.execute('SELECT * FROM student WHERE email = %s AND password = %s', (email, password, )) 
                account2 = mycursor.fetchone()
                if account2:
                    session['loggedin'] = True
                    session['id'] = account2[0] 
                    session['roll'] = account2[3]
                    session['username'] = account2[1] 
                    mycursor.execute("SELECT subject_name,subject_code FROM student_subject where roll_no=%s",(session['roll'],))
                    subj = mycursor.fetchall()
                    return render_template('student_dashboard.html', msg = subj,username=session['username'])
                else:
                    msg = 'Incorrect username / password !'
        return render_template('index.html', msg = msg)
    
    @app.route('/subject_choice',methods = ['POST','GET'])
    def subject_choice():
        msg=''
        if request.method == 'POST':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            ) 
            mycursor = mydb.cursor()
           
            semester = request.form['semester']
            mycursor.execute("SELECT subject_name FROM teacher_subject where semester= %s",(semester,))
            subject_name = mycursor.fetchall()

        return render_template('student_subject.html', msg=subject_name,username=session['username'])

    @app.route('/insert_sub',methods = ['POST','GET'])
    def insert_sub():
        msg=''
        if request.method == 'POST':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            ) 
            mycursor = mydb.cursor()
            selected = request.form.getlist('subject_list')
            for row in selected:
                 mycursor.execute('SELECT * FROM student_subject WHERE roll_no = %s AND subject_name = %s', (session['roll'], row, )) 
                 account = mycursor.fetchall() 
                 if account:
                     msg2=''
                 else:
                     mycursor.execute('SELECT subject_code FROM teacher_subject where subject_name=%s',(row,))
                     subjectCode = mycursor.fetchone()
                     mycursor.execute('INSERT INTO student_subject(subject_name,roll_no,subject_code) VALUES (%s,%s,%s)',(row,session['roll'],subjectCode[0]))
            
            mydb.commit()
        mycursor.execute("SELECT subject_name,subject_code FROM student_subject where roll_no=%s",(session['roll'],))
        subj = mycursor.fetchall()
        
        return render_template('student_dashboard.html', msg = subj,username=session['username'])
    
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
        msg = '' 
        if request.method == 'POST': 
            email = request.form['email'] 
            password = request.form['password'] 
            if (email=='onk@gmail.com' and password=='qwerty'):
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
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            )
            mycursor = mydb.cursor()
            typefile = request.form['semester']
            file = request.files['myfile']
            file.save(os.path.join(app.config["UPLOADS"], file.filename))
            csvname = file.filename
            xlrd.xlsx.ensure_elementtree_imported(False, None)
            xlrd.xlsx.Element_has_iter = True
            book = xlrd.open_workbook("C:/Users/Onkar/{0}".format(str(csvname)))
            sheet = book.sheet_by_name("Sheet1")
            if typefile == 'Student':
                query = """INSERT INTO studentreg(prno,firstname,lastname) VALUES (%s, %s, %s)"""
                for r in range(1, sheet.nrows):
                    pr = sheet.cell(r,0).value
                    fn = sheet.cell(r,1).value
                    ln = sheet.cell(r,2).value
                    values = (pr,fn,ln)
                    mycursor.execute(query, values)
            elif typefile == 'Teacher':
                query = """INSERT INTO teacherreg(trid,fname,lname) VALUES (%s, %s, %s)"""
                for r in range(1, sheet.nrows):
                    pr = sheet.cell(r,0).value
                    fn = sheet.cell(r,1).value
                    ln = sheet.cell(r,2).value
                    values = (pr,fn,ln)
                    mycursor.execute(query, values)
            mycursor.close()
            mydb.commit()
            mydb.close()
            return render_template("admin.html", msg="File Upload Successful!")
    
    @app.route('/genexcel')
    def genexcel():
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_db"
        )

        mycursor = mydb.cursor()
        SQLStatement2 = "SELECT roll_no,status from attendance"
        mycursor.execute(SQLStatement2)
        myresult = mycursor.fetchall()
        #output in bytes
        output = io.BytesIO()
        #create workbook object
        workbook = xlwt.Workbook()
        #add a sheet
        sh = workbook.add_sheet('Student Attendance')
        
        #add headers
        sh.write(0, 0, 'Roll No')
        sh.write(0, 1, 'Name')
        sh.write(0, 2, 'Attendance')
        
        idx = 0
        for row in myresult:
            mycursor.execute('SELECT fname FROM  student where rollno= %s',( row[0],))
            data = mycursor.fetchone()
            sh.write(idx+1, 0, row[0])
            sh.write(idx+1, 1, data[0])
            sh.write(idx+1, 2, row[1])
            idx = idx+1
        workbook.save(output)
        output.seek(0)
        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=student_attendance.xls"})
        msg = 'Attendance Saved!'
        mycursor.close()
        mydb.commit()
        mydb.close()
        return render_template('teacher_dashboard.html', msg = msg)
    
    @app.route('/subjectofteacher', methods=['POST', 'GET'])
    def subjectofteacher():
        msg = ''
        if request.method == 'POST':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            )
            mycursor = mydb.cursor()
            teacher_id = session['id']

            subject_name = request.form['subject_name']
            subject_code = request.form['subject_code']
            semester = request.form['semester']
            course = request.form['Course']

            # check if subject with teacher is already exists or not
            sql1 = "SELECT * FROM teacher_subject WHERE teacher_id = %s AND subject_code=%s"
            val1 = (teacher_id,subject_code)
            mycursor.execute(sql1, val1)
            account = mycursor.fetchone()
            if account:
                msg = 'Subject already exists !'
            else:
                # check if its a official/legit teacher
                #sql2 = "SELECT * FROM teacher_subject WHERE teacher_id = %s"
                #val2 = (teacher_id)
                #mycursor.execute(sql2, val2)
                #account2 = mycursor.fetchone()
                #if account2:
                mycursor.execute('INSERT INTO teacher_subject(teacher_id,subject_name,subject_code,semester,batch) VALUES (%s,%s,%s,%s,%s)',(teacher_id,subject_name,subject_code,semester,course))
                mydb.commit()
                msg = 'You have successfully registered the subject!'
                #else:
                    
                    #msg = 'Please contact system admin'
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        mycursor.execute("SELECT subject_name,subject_code,semester FROM teacher_subject where teacher_id=%s",(session['id'],))
        subj = mycursor.fetchall()
        mycursor.close()
        mydb.commit()
        
        return render_template('teacher_dashboard.html', username=session['username'],msg=subj)
    
    @app.route('/email1', methods = ['POST', 'GET'])
    def email1():
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_db"
        )
        msg=''
        mycursor = mydb.cursor()
        mycursor.execute("SELECT subject_name FROM teacher_subject where teacher_id= %s",(session['id'],))
        subject_name = mycursor.fetchall() 
        return render_template('sendmail1.html', msg=subject_name,username=session['username'])
    
    @app.route('/send_mail',methods=['POST','GET'])
    def send_mail():
      
        attend = [[0 for i in range(3)] for j in range(60)]
        days=0
        myresult2=""
        data1=""
        i=0
        a=[0]*60
        now = datetime.datetime.today()
        day=now.strftime("%m/%d/%Y")
        date_time=""
        if request.method == 'POST': 
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            )
            mycursor=mydb.cursor()
            mycursor2=mydb.cursor()
            batch = request.form['batch'] 
            subnm = request.form['subnm'] 
            #batch="batch2019"
            
            mycursor.execute('SELECT * FROM  attendance where subject_name= %s and batch=%s',( subnm ,batch,))
            data = mycursor.fetchall()  
            for row in data:
                attend[row[1]%100][0]=row[1]
                if(row[6]=='P'):
                    attend[row[1]%100][1]+=1
            
            mycursor2.execute('SELECT COUNT(DISTINCT date) from attendance where subject_name= %s ',( subnm , ))
            days = mycursor2.fetchone()  
            day=days[0]
            
            server=smtplib.SMTP_SSL("smtp.gmail.com",465)
            server.login("bodhitapatil@gmail.com", "bodhita@4B")
            mycursor3=mydb.cursor()
            for i in range(len(attend)):
                attend[i][2]=attend[i][1]/day*100
                percent=str(attend[i][2])
                roll=attend[i][0]
                email1 = mycursor3.execute("SELECT email FROM student where rollno = %s",(roll,))
                myresult2 = mycursor.fetchone()
                if myresult2:
                    email_id=myresult2[0]
                    msg="Attendance for this subject is ... "+percent+"%"
                    server.sendmail("bodhitapatil@gmail.com", email_id, msg)
  
            #msg = 'sent...' 
            #
            #mycursor2.execute(email1)
            #myresult = mycursor.fetchall()
            #for row in myresult:
             #   name = row[0]
            
              #  
            #server.quit()
            mycursor.execute("SELECT subject_name,subject_code,semester FROM teacher_subject where teacher_id=%s",(session['id'],))
            subj = mycursor.fetchall()
            mycursor2.close()
            mycursor.close()

        return render_template('teacher_dashboard.html',msg=subj,username=session['username'])
    
    @app.route('/addrec',methods = ['POST','GET'])
    def addrec():
        msg=''
        if request.method == 'POST':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            )
            mycursor = mydb.cursor()
            subject_name = request.form['subject_name']
            date = request.form['date']
            time = request.form['time']
            batch = request.form['batch']
            mycursor2 = mydb.cursor()
            status_a="A"
            mycursor2.execute("SELECT roll_no FROM student_subject where subject_name=%s",(subject_name,))
            rollno = mycursor2.fetchall()
            for row in rollno:
                mycursor.execute('INSERT INTO attendance(subject_name,date,time_slot,batch,roll_no,status) VALUES (%s,%s,%s,%s,%s,%s)',(subject_name,date,time,batch,row[0],status_a))
            
            mydb.commit()

            def RetreiveImages():
                SQLStatement2 = "SELECT rollno,image from student"
                mycursor.execute(SQLStatement2)
                myresult = mycursor.fetchall()
                for row in myresult:
                    name = row[0]
                    photo = row[1]
                    storefilepath = "C:/Users/Oggy/.spyder-py3/face_recog/images/{0}.jpg".format(str(name))
                    write_file(photo,storefilepath)
        
            def write_file(data, filepath):
                with open(filepath, "wb") as File:
                    File.write(data)
                File.close()
        

            RetreiveImages()

            path = 'C:/Users/Oggy/.spyder-py3/face_recog/images'
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
                            SQLStatement2 = "UPDATE attendance SET status=%s WHERE roll_no=%s"
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