import cv2
import numpy as np
import pyttsx3

vid=cv2.VideoCapture(0)
dim=320
thr=0.5
nms=0.3

cf = 'coco.names'
cn=[]
with open(cf,'rt') as f:
    cn = f.read().rstrip('\n').split('\n')

mc = 'yolov3-tiny.cfg'
mw = 'yolov3-tiny.weights'

nt=cv2.dnn.readNetFromDarknet(mc,mw)
nt.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
nt.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

def cam(op,img):
    ha,wa,ca=img.shape
    bx=[]
    cid=[]
    con=[]

    for i in op:
        for h in i:
            sc=h[5:]
            ci=np.argmax(sc)
            conf=sc[ci]
            if conf > thr:
                wi=int(h[2]*wa)
                hi=int(h[3]*ha)
                x=int((h[0]*wa)-wi/2)
                y=int((h[1]*ha)-hi/2)
                bx.append([x,y,wi,hi])
                cid.append(ci)
                con.append(float(conf))

    ind=cv2.dnn.NMSBoxes(bx,con,thr,nms)
    print(ind)
    for q in ind:
        if isinstance(q, (list, tuple)) and len(q) > 0:
            q = q[0]
        berks = bx[q]
        x, y, w, h = berks[0], berks[1], berks[2], berks[3]


        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(img,f'{cn[cid[q]].upper()}{int(con[q]*100)}%',
                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        var = f'{cn[cid[q]].upper()}'
        print (var)

        engine = pyttsx3.init()
        engine.say(var)
        engine.runAndWait()

while True:
    success, img=vid.read()
    blb=cv2.dnn.blobFromImage(img, 1/255, (dim,dim), [0,0,0],1,crop=False)
    nt.setInput(blb)

    ln=nt.getLayerNames()
    on=[ln[i-1] for i in nt.getUnconnectedOutLayers()]

    op=nt.forward(on)
    cam(op,img)
    cv2.imshow('image', img)
    if cv2.waitKey(1) == ord("q"):
        break

