import datetime
import MySQLdb
from DB1 import UpSQL

def data_out_txt(plate_info):
	timeIn=datetime.datetime.now()
	info='Bien so:' + plate_info +' ,  Thoi gian:'+timeIn.strftime("%c")+'\n'
	file_out=open('Data_input.txt','a+')
	file_out.write(info) 
	x=timeIn.strftime("%c")
	UpSQL(plate_info,x)
