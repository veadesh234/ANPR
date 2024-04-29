import os
import cv2
from datetime import datetime as dt
import easyocr
import mysql.connector
count=0                                     #initialized for saving temp images

states={"AN":"Andaman and Nicobar", "AP":"Andhra Pradesh", "AR":"Arunachal Pradesh", "AS":"Assam", "BR":"Bihar", "CH":"Chandigarh", "DN":"Dadra and Nagar Haveli", "DD":"Daman and Diu","DL":"Delhi", "GA":"Goa", "GJ":"Gujarat", "HR":"Haryana", "HP":"Himachal Pradesh", "JK":"Jammu and Kashmir", "KA":"Karnataka", "KL":"Kerala", "LD":"Lakshadweep", "MP":"Madhya Pradesh", "MH":"Maharashtra", "MN":"Manipur", "ML":"Meghalaya", "MZ":"Mizoram", "NL":"Nagaland", "OD":"Odissa", "PY":"Pondicherry", "PN":"Punjab", "RJ":"Rajasthan", "SK":"Sikkim", "TN":"TamilNadu", "TR":"Tripura", "UP":"Uttar Pradesh", "WB":"West Bengal", "CG":"Chhattisgarh", "TS":"Telangana", "JH":"Jharkhand", "UK":"Uttarakhand"}

def orb_sim(img1, img2):                 #func for checking similarity of images
    orb = cv2.ORB_create()                          
    kp_a, desc_a = orb.detectAndCompute(img1, None)
    kp_b, desc_b = orb.detectAndCompute(img2, None)     
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)   
    matches = bf.match(desc_a, desc_b)                      #perform matches.
    similar_regions = [i for i in matches if i.distance < 50]       
    if len(matches) == 0:
        return 0
    return len(similar_regions) / len(matches)
def checkperm():                                                        
    is_similar = False
    directory = os.listdir("D:\\Image_perm")
    if len(directory) == 0:
        image_path = "D:\\Number_plates\\Image"+str(count)+".jpg"
        img_save= cv2.imread(image_path)
        cv2.imwrite("D:\\Image_perm\\"+str_rep+".jpg",img_save)
    else:
        for images in os.listdir("D:\\Image_perm"):
            img1=cv2.imread("D:\\Number_plates\\Image"+str(count)+".jpg")
            img2=cv2.imread("D:/Image_perm/"+ images)
            similarity = orb_sim(img1,img2)
	  
            if similarity <= 0.60:
                pass
            else:
                is_similar = True
                break
    return is_similar
def ocr(c):                                             
    img = cv2.imread('D:\\Number_plates\\Image'+str(c)+'.jpg')
    reader = easyocr.Reader(['en'])
    result = reader.readtext(img)
    text = result[0][-2]
    text= ''.join(e for e in text if e.isalnum())
    text_cap = text.upper()
    print(text_cap)
    stat = text_cap[0:2]
    try:
        state = states[stat]
        print('Car Belongs to',state)
    except:
        state ="SNR"
        print('State not recognised!!')
    myCursor.execute("INSERT INTO ANPR (PLATE_CHAR, STATE) VALUES (%s, %s)", (text_cap, state))
    mycon.commit()
try:
    mycon=mysql.connector.connect(host='localhost',user='root',passwd='V')
    myCursor=mycon.cursor()
    myCursor.execute("CREATE DATABASE IF NOT EXISTS ANPR_SYS")
    myCursor.execute("USE ANPR_SYS")
    myCursor.execute("CREATE TABLE IF NOT EXISTS ANPR (DATE_TIME TIMESTAMP NOT NULL DEFAULT current_timestamp on update current_timestamp,PLATE_CHAR VARCHAR(15),STATE VARCHAR(30))")
except Exception as e:
    print(e)
plateCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_russian_plate_number.xml")
minArea = 500
cap =cv2.VideoCapture(0)
while True:
    success , img  = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    numberPlates = plateCascade.detectMultiScale(imgGray, 1.1, 4)   #number plate recognition
    for (x, y, w, h) in numberPlates:
        area = w*h
        if area > minArea:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img,"NumberPlate",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
            imgRoi = img[y:y+h,x:x+w]                               #crop number plate
            cv2.imshow("ROI",imgRoi)
    cv2.imshow("Result",img)
    if cv2.waitKey(1) & 0xFF ==ord('s'):#press s to save image in temp director
        cv2.imwrite("D:\\Number_plates\\Image"+str(count)+".jpg",imgRoi)
        c = checkperm()
        if c == False:
            now = dt.now()
            str_now = str(now)
            str_rep = str_now.replace(':','.')
            image_path = "D:\\Number_plates\\Image"+str(count)+".jpg"
            img_save= cv2.imread(image_path)
            cv2.imwrite("D:\\Image_perm\\"+str_rep+".jpg",img_save)
            print("image saved")
        cv2.rectangle(img,(0,200),(640,300),(0,255,0),cv2.FILLED)
        cv2.putText(img,"Scan Saved",(15,265),cv2.FONT_HERSHEY_COMPLEX,2,(0,0,255),2)
        cv2.imshow("Result",img)
        cv2.waitKey(500)
        ocr(count)
        count+=1
    if cv2.waitKey(1) & 0xFF ==ord('e'):                 #press e to write queries
        try:
            qry = input("ENTER SELECT TABLE QUERY:")
            myCursor.execute(qry)
            myr = myCursor.fetchall()
            for x in myr:
                print(x)
        except Exception as e:
            print(e)
    if cv2.waitKey(1) & 0xFF ==ord('q'):#press q to quit and close the windows
        break
cap.release()
cv2.destroyAllWindows()
