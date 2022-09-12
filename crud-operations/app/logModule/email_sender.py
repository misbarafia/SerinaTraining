import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def send_mail(sender,receipients,subject,body):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receipients
    msg['Subject'] = subject
    #body = f"<html><body><b>Cannot process file : {filename}, File type {filetype} not supported</b></body></html>"
    msg.attach(MIMEText(body, 'html'))
    # put your relevant SMTP here
    server = smtplib.SMTP('smtp.office365.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(os.getenv("MAIL_USERNAME",default="serinaplus.dev@datasemantics.co"),os.getenv("MAIL_PASSWORD","ravager55@rocket"))  # if applicable
    server.send_message(msg)
    server.quit()