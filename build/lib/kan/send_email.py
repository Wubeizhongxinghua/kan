import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import click
import toml
import os
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_path)
from exceptions import ConfigAbnormalError
def send_email(config_file=None, host=None, port=25, user=None, passwd=None, sender=None, receivers=[], title="An email", context='No context here.'):
	if config_file is not None:
		settings = toml.load(config_file)
		host = settings['sends']['host']
		user = settings['sends']['user']
		passwd = settings['sends']['passwd']
		sender = settings['sends']['sender']
		port = settings['sends']['port']
		receivers = settings['receivers']['receivers']
		title = settings['contexts']['title']
		context = settings['contexts']['context']
	message = MIMEText(context, 'plain', 'utf-8')
	message['From'] = sender
	try:
		message['To'] = receivers[0]
	except:
		print("Seems your config is abnormal. You'd better re-check your config.")
	message['Subject'] = title

	try:
		smtpObj = smtplib.SMTP(host, port)
		smtpObj.connect(host, port)
		smtpObj.ehlo()
		smtpObj.starttls()
		smtpObj.login(user, passwd)
		smtpObj.sendmail(
			sender,
			receivers,
			message.as_string()
		)
		smtpObj.quit()
		print(f'Email sent: From \033[4m{sender}\033[0m To \033[4m{receivers}\033[0m.')
		print(f"\033[1m{title}\033[0m")
		print(f"\033[2m{context}\033[0m")
	except smtplib.SMTPException as e:
		print('An error occured when sending email.',e)


def server_connect(config_file=None, host=None, port=25, user=None, passwd=None, sender=None):
	if config_file is not None:
		settings = toml.load(config_file)
		host = settings['sends']['host']
		user = settings['sends']['user']
		passwd = settings['sends']['passwd']
		sender = settings['sends']['sender']
		port = settings['sends']['port']
	try:
		print(f"Try connecting...")
		smtpObj = smtplib.SMTP(host, port)
		smtpObj.connect(host, port)
		smtpObj.ehlo()
		smtpObj.starttls()
		smtpObj.login(user, passwd)
		smtpObj.quit()
		print("Test connection successfully!")
	except Exception as e:
		print()
		print(f"Seems the combination of host, port, user, passwd you provided cannot connect successfully:")
		print(e)
		sys.exit()
