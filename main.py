
import speech_recognition as sr
import datetime
import pyttsx3
import webbrowser
import mysql.connector

from tkinter import *
from PIL import Image

mydb = mysql.connector.connect(host='localhost', user='root', password='', database='1e_system')
mycursor = mydb.cursor()

root = Tk()
root.geometry("800x550")
root.config(background="black")
root.resizable(False,False)

gifImage = "bla.gif"
open_image = Image.open(gifImage)

frames = open_image.n_frames

imageObject = [PhotoImage(file=gifImage, format=f"gif -index {i}") for i in range(frames)]

count = 0

showAnimation = None


def animation(count):
    global showAnimation
    newImage = imageObject[count]

    gif_label.configure(image=newImage)
    count += 1

    if count == frames:
        count = 0
    showAnimation = root.after(50, lambda: animation(count))


def word(e):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    recognizer = sr.Recognizer()

    engine.say("hellow sir")
    engine.runAndWait()

    def cmd():

        with sr.Microphone() as source:
            print("Clearing background noises...Pleasw wait")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            engine.say('What do you want..')
            engine.runAndWait()
            recordedaudio = recognizer.listen(source)
        try:

            text = recognizer.recognize_google(recordedaudio, language='en_US')
            text = text.lower()
            print('Your message:', format(text))

        except Exception as ex:
            print(ex)

        if 'identify' in text:
            time = datetime.datetime.now().strftime('%I:%M %p')
            sql = "INSERT INTO activity_logs (command,time) VALUES (%s,%s)"
            val = (text, time)
            mycursor.execute(sql, val)
            mydb.commit()
            engine.say("identifying Face")
            engine.runAndWait()
            import cv2
            import numpy as np
            import pyttsx3


            vid = cv2.VideoCapture(0)
            dim = 320
            thr = 0.5
            nms = 0.3

            cf = 'coco.names'
            cn = []
            with open(cf, 'rt') as f:
                cn = f.read().rstrip('\n').split('\n')

            mc = 'yolov3-tiny.cfg'
            mw = 'yolov3-tiny.weights'



            nt = cv2.dnn.readNetFromDarknet(mc, mw)
            nt.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            nt.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

            def cam(op, img):
                ha, wa, ca = img.shape
                bx = []
                cid = []
                con = []
                global dect



                for i in op:
                    for h in i:
                        sc = h[5:]
                        ci = np.argmax(sc)
                        conf = sc[ci]
                        if conf > thr:
                            wi = int(h[2] * wa)
                            hi = int(h[3] * ha)
                            x = int((h[0] * wa) - wi / 2)
                            y = int((h[1] * ha) - hi / 2)
                            bx.append([x, y, wi, hi])
                            cid.append(ci)
                            con.append(float(conf))

                ind = cv2.dnn.NMSBoxes(bx, con, thr, nms)
                print(ind)
                for q in ind:
                    if isinstance(q, (list, tuple)) and len(q) > 0:
                        q = q[0]
                    berks = bx[q]
                    x, y, w, h = berks[0], berks[1], berks[2], berks[3]

                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(img, f'{cn[cid[q]].upper()}{int(con[q] * 100)}%',
                                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                    var = f'{cn[cid[q]]}'
                    dect =var
                    engine = pyttsx3.init()
                    engine.say(var)
                    engine.runAndWait()


            while True:
                success, img = vid.read()
                blb = cv2.dnn.blobFromImage(img, 1 / 255, (dim, dim), [0, 0, 0], 1, crop=False)
                nt.setInput(blb)

                ln = nt.getLayerNames()
                on = [ln[i - 1] for i in nt.getUnconnectedOutLayers()]

                op = nt.forward(on)
                cam(op, img)
                cv2.imshow('image', img)
                if cv2.waitKey(1) == ord("q"):
                    break
            sql = "insert into objects_identified(objects)value(%s);"

            mycursor.execute(sql,dect)
            mydb.commit()

        if text == 'time':
            time = datetime.datetime.now().strftime('%I:%M %p')
            print(time)
            engine.say(time)
            engine.runAndWait()
            sql = "INSERT INTO activity_logs (command,time) VALUES (%s,%s)"
            val = (text,time)
            mycursor.execute(sql, val)
            mydb.commit()
        if text == 'radio':
            a = 'opening Radio..'
            time = datetime.datetime.now().strftime('%I:%M %p')
            engine.say(a)
            engine.runAndWait()
            webbrowser.open('https://www.youtube.com/watch?v=wvIhGsX1rTI')
            sql = "INSERT INTO activity_logs (command,time) VALUES (%s,%s)"
            val = (text,time)
            mycursor.execute(sql, val)
            mydb.commit()

        if text == 'youtube':
            time = datetime.datetime.now().strftime('%I:%M %p')
            b = 'opening youtube'
            engine.say(b)
            engine.runAndWait()
            webbrowser.open('www.youtube.com')
            sql = "INSERT INTO activity_logs (command,time) VALUES (%s,%s)"
            val = (text, time)
            mycursor.execute(sql, val)
            mydb.commit()

    cmd()


gif_label = Label(root, image="", bg="Black")
root.bind('<Key>', word)

gif_label.place(x=190, y=20, width=450, height=500)

animation(count)

root.mainloop()