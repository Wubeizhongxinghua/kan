import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import click
import toml
@click.command()
@click.option('-c','--config_file',default=None,help="""[RECOMMENDED] Config file (.toml) including the following parameters. If set, the followings won\'t change what\'s been set here.""")
@click.option('-h','--host',default=None,help="SMTP server address.")
@click.option('-d','--port',default=25,help="SMTP port.")
@click.option('-u','--user',default=None,help='Username of sender email account.')
@click.option('-p','--passwd',default=None,help='Password or token of sender email account.')
@click.option('-s','--sender',default=None,help='Email address of sender.')
@click.option('-r','--receivers',default=[],help='List of receivers\' email addresses.',multiple=True)
@click.option('-t','--title',default="An email",help='Title of the email.')
@click.option('-o','--context',default="No context here.",help='Context of the email.')

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
	message['To'] = receivers[0]
	message['Subject'] = title

	try:
		smtpObj = smtplib.SMTP()
		smtpObj.connect(host, port)
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
		print('An error occured.',e)
	


if __name__=='__main__':
	send_email()

