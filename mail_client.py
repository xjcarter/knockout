
#!/usr/bin/python
# Adapted from http://kutuma.blogspot.com/2007/08/sending-emails-via-gmail-with-python.html

import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import pandas
import time

gmail_user = "xjcarter@gmail.com"
gmail_pwd = "Bl@ckpanther" 

test_html = """
<html>
<head>
</head>
<body>
<div class="rules_div>
<div class="rule_header"><p>Three Little Pigs</p></div>
<div class="rules">
<ol>
<li>One little piggy</li>
<li>Twp little piggy</li>
<li>Three little piggy</l>
</ol>
</div>
</div>
</body>
</html>
"""

def login(user):
	global gmail_user, gmail_pwd
	gmail_user = user
	gmail_pwd = getpass.getpass('Password for %s: ' % gmail_user)

def mail(to, subject, text, html=None, attach=None):
	msg = MIMEMultipart()
	msg['From'] = gmail_user
	msg['To'] = to
	msg['Subject'] = subject
	msg.attach(MIMEText(text))
	if html:
		msg.attach(MIMEText(html,"html"))
	if attach:
		part = MIMEBase('application', 'octet-stream')
		part.set_payload(open(attach, 'rb').read())
		encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
		msg.attach(part)
	mailServer = smtplib.SMTP("smtp.gmail.com", 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(gmail_user, gmail_pwd)
	mailServer.sendmail(gmail_user, to, msg.as_string())
	mailServer.close()

if __name__ == '__main__':
	mail('xjcarter@gmail.com','Test',"Hello J!",html=test_html)

