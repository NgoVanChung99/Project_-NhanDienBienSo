
import cv2
import numpy as np
import datetime
from txtdata import data_out_txt
from lib_detection import load_model, detect_lp, im2single
from Camera import layAnh_Camera
from CheckMail import CheckMail
from SendMail import Sendmail
#from DB1 import UpSQL

# Ham sap xep contour tu trai sang phai
def sort_contours(cnts):

    reverse = False
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return cnts

# Dinh nghia cac ky tu tren bien so
char_list =  '0123456789ABCDEFGHKLMNPRSTUVXYZ'

# Ham fine tune bien so, loai bo cac ki tu khong hop ly
def fine_tune(lp):
    newString = ""
    for i in range(len(lp)):
        if lp[i] in char_list:
            newString += lp[i]
    return newString

while True :
     layAnh_Camera()
     img_path = "C:/Users/chungPC/Desktop/Project_ANPR/filename.jpg"
     # Load model LP detection
     wpod_net_path = "wpod-net_update1.json"
     wpod_net = load_model(wpod_net_path)
    
     # Đọc file ảnh đầu vào
     Ivehicle = cv2.imread(img_path)

     try:
         Ivehicle.shape
         print("checked for shape".format(Ivehicle.shape))
     except AttributeError:
           print("shape not found")
     #print (Ivehicle)
     # Kích thước lớn nhất và nhỏ nhất của 1 chiều ảnh
     Dmax = 608
     Dmin = 288

     # Lấy tỷ lệ giữa W và H của ảnh và tìm ra chiều nhỏ nhất
     ratio = float(max(Ivehicle.shape[:2])) / min(Ivehicle.shape[:2])
     side = int(ratio * Dmin)
     bound_dim = min(side, Dmax)
     #print("ratio :",max(Ivehicle.shape[:2]))

     try:
         _ , LpImg, lp_type = detect_lp(wpod_net, im2single(Ivehicle), bound_dim, lp_threshold=0.5)
     except :
          print("bien so null")          
          #break
          #quit()
     try :
             # Cau hinh tham so cho model SVM
             digit_w = 30 # Kich thuoc ki tu
             digit_h = 60 # Kich thuoc ki tu

             model_svm = cv2.ml.SVM_load('svm.xml')
             timeIn=datetime.datetime.now()
             if (len(LpImg) and lp_type==1):                
                 #cv2.imshow("Anh sau cat",cv2.cvtColor(LpImg[0],cv2.COLOR_BGR2GRAY))
                 # Chuyen doi anh bien so
                 LpImg[0] = cv2.convertScaleAbs(LpImg[0], alpha=(255.0))

                 roi = LpImg[0]
                 #cv2.imshow("Anh bien so",roi)
                 # Chuyen anh bien so ve gray
                 gray = cv2.cvtColor( LpImg[0], cv2.COLOR_BGR2GRAY)


                 # Ap dung threshold de phan tach so va nen
                 binary = cv2.threshold(gray, 127, 255,
                         cv2.THRESH_BINARY_INV)[1]

                 #cv2.imshow("Anh bien so sau threshold", binary)
                 #cv2.waitKey()

                 # Segment kí tự
                 kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                 thre_mor = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel3)
                 cont, _  = cv2.findContours(thre_mor, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


                 plate_info = ""
                 #i=0

                 for c in sort_contours(cont):
                     (x, y, w, h) = cv2.boundingRect(c)
                     ratio = h/w
                     if 1.5<=ratio<=3.5: # Chon cac contour dam bao ve ratio w/h
                         if h/roi.shape[0]>=0.6: # Chon cac contour cao tu 60% bien so tro len

                             # Ve khung chu nhat quanh so
                             #cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                             # Tach so va predict
                             curr_num = thre_mor[y:y+h,x:x+w]
                             #i+=1
                             #title='Anh so'+ str(i)
                             #cv2.imshow(title,curr_num)
                             curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                             _, curr_num = cv2.threshold(curr_num, 30, 255, cv2.THRESH_BINARY)
                             curr_num = np.array(curr_num,dtype=np.float32)
                             curr_num = curr_num.reshape(-1, digit_w * digit_h)
                             #print("vector :",curr_num)

                             # Dua vao model SVM

                             result = model_svm.predict(curr_num)[1]
                             result = int(result[0, 0])

                             if result<=9: # Neu la so thi hien thi luon
                                 result = str(result)
                             else: #Neu la chu thi chuyen bang ASCII
                                 result = chr(result)

                             plate_info +=result

                 #cv2.imshow("Cac contour tim duoc", roi)
                 #cv2.waitKey()

                 # Viet bien so len anh
                 #cv2.putText(Ivehicle,fine_tune(plate_info),(50, 50), cv2.FONT_HERSHEY_PLAIN, 3.0, (0, 0, 255), lineType=cv2.LINE_AA)

                 #Luu bien so va thoi gian vao file txt
                 data_out_txt(plate_info)
                 print("mail: ",CheckMail(plate_info))
                 mail=CheckMail(plate_info)
                 x=timeIn.strftime("%c")
                 if mail!="ko co":
                    Sendmail(mail,x,plate_info)
                 else:
                    print("Khong co chu xe")

                 #CheckMail(plate_info)
                 # Hien thi anh
                 print("Bien so=", plate_info)
                 #cv2.imshow("Hinh anh output",Ivehicle)
                 #cv2.waitKey()

             else :
                if (len(LpImg) and lp_type==2):
                     #print("Bien 2 dong 1")
                     #cv2.imshow("Anh sau cat",cv2.cvtColor(LpImg[0],cv2.COLOR_BGR2GRAY))
                     LpImg[0] = cv2.convertScaleAbs(LpImg[0], alpha=(255.0))
                     
                     grayV = cv2.cvtColor( LpImg[0], cv2.COLOR_BGR2GRAY)
                     binaryV = cv2.threshold(grayV, 127, 255,
                         cv2.THRESH_BINARY_INV)[1]
                     
                     plate_info = ""
                     x=0
                     y=0
                     w=binaryV.shape[0]-100
                     h=binaryV.shape[1]
                     crop1=binaryV[y:w,x:h]
                     _roiV = LpImg[0]
                     roiV=_roiV[y:w,x:h]
                     #cv2.imshow("Anh chia dong 1",crop1)
                     kernel3_1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                     thre_mor1 = cv2.morphologyEx(crop1, cv2.MORPH_DILATE, kernel3_1)
                     cont1, _  = cv2.findContours(thre_mor1, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                     for c in sort_contours(cont1):
                         (x, y, w, h) = cv2.boundingRect(c)
                         ratio = h/w
                         if 1.5<=ratio<=3.5: # Chon cac contour dam bao ve ratio w/h
                             if h/roiV.shape[0]>=0.6: # Chon cac contour cao tu 60% bien so tro len

                                 # Ve khung chu nhat quanh so
                                 #cv2.rectangle(roiV, (x, y), (x + w, y + h), (0, 255, 0), 2)

                                 # Tach so va predict
                                 curr_num = thre_mor1[y:y+h,x:x+w]
                                 curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                                 _, curr_num = cv2.threshold(curr_num, 30, 255, cv2.THRESH_BINARY)
                                 curr_num = np.array(curr_num,dtype=np.float32)
                                 curr_num = curr_num.reshape(-1, digit_w * digit_h)
                             

                                 # Dua vao model SVM

                                 result = model_svm.predict(curr_num)[1]
                                 result = int(result[0, 0])

                                 if result<=9: # Neu la so thi hien thi luon
                                     result = str(result)
                                 else: #Neu la chu thi chuyen bang ASCII
                                     result = chr(result)

                                 plate_info +=result
                     #cv2.imshow("Anh bien so sau threshold 2 dong ", binaryV)
                     #cv2.imshow("Cac contour tim duoc 1", roiV)

                     crop2=binaryV[100:200,0:280]
                     #cv2.imshow("Anh chia dong 2",crop2)

                     #roiV1 = LpImg[0]
                     _roiv1=LpImg[0]
                     roiV1=_roiv1[100:200,0:280]
                     kernel3_2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                     thre_mor2 = cv2.morphologyEx(crop2, cv2.MORPH_DILATE, kernel3_2)
                     cont2, _  = cv2.findContours(thre_mor2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                     for c in sort_contours(cont2):
                         (x, y, w, h) = cv2.boundingRect(c)
                         ratio = h/w
                         if 1.5<=ratio<=3.5: # Chon cac contour dam bao ve ratio w/h
                             if h/roiV1.shape[0]>=0.6: # Chon cac contour cao tu 60% bien so tro len

                                 # Ve khung chu nhat quanh so
                                 #cv2.rectangle(roiV1, (x, y), (x + w, y + h), (0, 255, 0), 2)

                                 # Tach so va predict
                                 curr_num = thre_mor2[y:y+h,x:x+w]
                                 curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                                 _, curr_num = cv2.threshold(curr_num, 30, 255, cv2.THRESH_BINARY)
                                 curr_num = np.array(curr_num,dtype=np.float32)
                                 curr_num = curr_num.reshape(-1, digit_w * digit_h)
                             

                                 # Dua vao model SVM

                                 result = model_svm.predict(curr_num)[1]
                                 result = int(result[0, 0])

                                 if result<=9: # Neu la so thi hien thi luon
                                     result = str(result)
                                 else: #Neu la chu thi chuyen bang ASCII
                                     result = chr(result)

                                 plate_info +=result

                     #cv2.imshow("Cac contour tim duoc 2", roiV1)
                     print("Bien so:",plate_info)
                     #Luu bien so va thoi gian vao file txt
                     data_out_txt(plate_info)
                     
                     #UpSQL(plate_info)
                     print("mail: ",CheckMail(plate_info))
                     mail=CheckMail(plate_info)
                     x1=timeIn.strftime("%c")
                     #if mail!="ko co":
                        #Sendmail(mail,x1,plate_info)
                     #else:
                        #print("Khong co chu xe")

                     #cv2.putText(Ivehicle,fine_tune(plate_info),(50, 50), cv2.FONT_HERSHEY_PLAIN, 3.0, (0, 0, 255), lineType=cv2.LINE_AA)
                     #cv2.imshow("Hinh anh output",Ivehicle)
                     #cv2.waitKey()

                     #cv2.imshow("anh abc",roiV)
                     #print("Bien 2 dong 2")
                     


     except:
        print("------")




cv2.destroyAllWindows()
