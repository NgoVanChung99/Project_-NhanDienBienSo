import csv
import MySQLdb

def CheckMail(BS):
     mydb = MySQLdb.connect("localhost","root","12345678","test")                                            
     mycursor = mydb.cursor()
     mycursor.execute("SELECT * FROM user") 
     myresult = mycursor.fetchall()
     #print (BS)
     #print (myresult)
     y=''
     for x in myresult:
     	 #print (x[0])
     	 if BS==x[0]:
     	 	y=x[1]
     	 	break
     if y=="":
          y="ko co"

     #print(y)
     return y

        
#x='43A27208'
#CheckMail(x)




