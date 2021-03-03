# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 18:39:31 2021

@author: Onkar
"""

from flask import Flask, render_template, request, Response
import mysql.connector
import cv2
import numpy as np
import face_recognition
import os

app = Flask(__name__)

class req:
    @app.route('/')
    def home():
        return render_template('Ui.html')
    
    @app.route('/addrec',methods = ['POST','GET'])
    def addrec():
        if request.method == 'POST':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="attendance_db"
            )

            mycursor = mydb.cursor()

            def RetreiveImages():
                SQLStatement2 = "SELECT username,image from student"
                mycursor.execute(SQLStatement2)
                myresult = mycursor.fetchall()
                for row in myresult:
                    name = row[0]
                    photo = row[1]
                    storefilepath = "C:/Users/Onkar/.spyder-py3/face_recog/images/{0}.jpg".format(str(name))
                    write_file(photo,storefilepath)
        
            def write_file(data, filepath):
                with open(filepath, "wb") as File:
                    File.write(data)
                File.close()
        

            RetreiveImages()

            path = 'C:/Users/Onkar/.spyder-py3/face_recog/images'
            imgList = []
            personNames = []
            myList = os.listdir(path)
            print(myList)
            for cls in myList:
                curImg = cv2.imread(f'{path}/{cls}')
                imgList.append(curImg)
                personNames.append(os.path.splitext(cls)[0])
            #print(personNames)

            def findEncodings(imgList):
                encodeList = []
                for img in imgList:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    encode = face_recognition.face_encodings(img)[0]
                    encodeList.append(encode)
                return encodeList

            encodeListStoredImages = findEncodings(imgList)
            #print(len(encodeListStoredImages))  
            

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
            
        
#faceloc = face_recognition.face_locations(imgBill)[0]
#encodeBill = face_recognition.face_encodings(imgBill)[0]
#cv2.rectangle(imgBill,(faceloc[3],faceloc[0]),(faceloc[1],faceloc[2]),(255,0,255),2)

#facelocTest = face_recognition.face_locations(imgTest)[0]
#encodeTest = face_recognition.face_encodings(imgTest)[0]
#cv2.rectangle(imgTest,(facelocTest[3],facelocTest[0]),(facelocTest[1],facelocTest[2]),(255,0,255),2)

#results = face_recognition.compare_faces([encodeBill], encodeTest)
#faceDis = face_recognition.face_distance([encodeBill], encodeTest)