import sys
from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
# old version
# from email.MIMEText import MIMEText
from email.mime.text import MIMEText
from CheckMail import CheckMail

#x='43A27208'
#y=CheckMail(x)
def Sendmail(mail,time,BienSo):
    SMTP_Host = 'smtp.gmail.com'
    sender = 'dinhan0209@gmail.com'
    receivers = [mail]
    #receivers=y
    username = "dinhan0209@gmail.com"
    password = "eypoliclgwxxhlyl"
    # typical values for text_subtype are plain, html, xml
    text_subtype = 'plain'
    content = "Xe:"+BienSo+" check in :"+time+" "
    #content=" check xe"
    subject = "Thong bao nha xe"
    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject'] = subject
        msg['From'] = sender  # some SMTP servers will do this automatically, not all
        conn = SMTP(SMTP_Host)
        conn.set_debuglevel(False)
        conn.login(username, password)
        try:
            conn.sendmail(sender, receivers, msg.as_string())
            print("Sent")
        finally:
            conn.quit()
    except Exception as error:
        print(error)

