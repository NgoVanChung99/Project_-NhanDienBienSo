import csv
import MySQLdb
#import mysql.connector


def UpSQL(BS,TG):
     mydb = MySQLdb.connect("localhost","root","12345678","test")                                            
     mycursor = mydb.cursor()
     sql = "INSERT INTO bienso (BienSo, ThoiGian) VALUES (%s, %s)"
     val = (BS, TG)
     mycursor.execute(sql, val)
     mydb.commit()
     print("1 record inserted ")

     




