import sys
import click
from absl import app
import os
import time
import toml
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_path)
from job_monitor import pkushow
from job_monitor import pkusq
from job_monitor import pidinfo
from send_email import send_email
from send_webhook import send_webhook
from send_email import server_connect
from exceptions import ConfigNotFoundError
from exceptions import ConfigAbnormalError

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
	if ctx.invoked_subcommand is None:
		ctx.invoke(job)

@main.command()
@click.argument('jobid')
@click.option('-f','--frequency',default=60,help='Interval of checking whether the job is accomplished. default: 60s')
@click.option('-c','--config',default=None, help="Config used to send email. If not set, the default config will be used. Use \"kan list_config\" to see all valid configs.")
def tsk(jobid, frequency, config):
	"""Monitor a cluster task, and send email to remind if finished."""
	def get_filenames_without_extension(directory_path):
		filenames = []
    
		for filename in os.listdir(directory_path):
			if os.path.isfile(os.path.join(directory_path, filename)):
				name_without_extension = os.path.splitext(filename)[0]
				filenames.append(name_without_extension)
		return filenames
	try:
		configpath = f"{base_path}/config"
		configs = get_filenames_without_extension(configpath)
		
		jobinfo = ''.join(pkushow(jobid))
		
		if config is None: #use default
			theconfig = toml.load(f'{base_path}/settings.toml')
			
		elif config in configs:
			theconfig = toml.load(f'{configpath}/{config}.toml')
		else:
			raise ConfigNotFoundError(config)
			
			
		#持续搜索此任务
		while True:
			try:
				jobtime = pkusq(jobid).__next__()
			except:
				break
			time.sleep(frequency)

		theconfig['contexts']['title'] = f'[KAN remind] Submitted task {jobid} finished.'
		theconfig['contexts']['context'] = f"""
Task {jobid} finished at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.
The task has been running for {jobtime} (±{frequency}s).
The detailed information of the task is:
{jobinfo}
		"""
	except:
		raise ConfigAbnormalError(config)
	temp_cfg = f"{base_path}/{hash(time.time())}.toml"
	with open(temp_cfg, 'w') as f:
		toml.dump(theconfig, f)
	if theconfig['type']['type'] == 'email':
		send_email(config_file=temp_cfg)
	if theconfig['type']['type'] == 'webhook':
		send_webhook(config_file=temp_cfg)
	os.remove(temp_cfg)			
        	

@main.command()
@click.argument('pid')
@click.option('-f','--frequency',default=60,help='Interval of checking whether the job is accomplished. default: 60s')
@click.option('-c','--config',default=None, help="Config used to send email. If not set, the default config will be used. Use \"kan list_config\" to see all valid configs.")
def job(pid, frequency, config):
	"""Monitor a shell job, and send email to remind if finished."""
	def get_filenames_without_extension(directory_path):
		filenames = []
    
		for filename in os.listdir(directory_path):
			if os.path.isfile(os.path.join(directory_path, filename)):
				name_without_extension = os.path.splitext(filename)[0]
				filenames.append(name_without_extension)
		return filenames
	try:
		configpath = f"{base_path}/config"
		configs = get_filenames_without_extension(configpath)
		
		#jobinfo = ''.join(pkushow(jobid))
		
		if config is None: #use default
			theconfig = toml.load(f'{base_path}/settings.toml')
			
		elif config in configs:
			theconfig = toml.load(f'{configpath}/{config}.toml')
		else:
			raise ConfigNotFoundError(config)
			
			
		#持续搜索此任务
		while True:
			try:
				starttime, command = pidinfo(pid).__next__()
			except:
				break
			time.sleep(frequency)

		theconfig['contexts']['title'] = f'[KAN remind] Job {pid} finished.'
		theconfig['contexts']['context'] = f"""
Job {pid} finished at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.
The job started at {starttime}.
The command of the job is:
{command}
		"""
	except:
		raise ConfigAbnormalError(config)
	temp_cfg = f"{base_path}/{hash(time.time())}.toml"
	with open(temp_cfg, 'w') as f:
		toml.dump(theconfig, f)
	if theconfig['type']['type'] == 'email':
		send_email(config_file=temp_cfg)
	if theconfig['type']['type'] == 'webhook':
		send_webhook(config_file=temp_cfg)
	os.remove(temp_cfg)			

@main.command()
@click.argument('name')
@click.option('-t','--config_type',default='email', required = True, type=click.Choice(['email','webhook']), help="Type of config, options: ['email','webhook']")
@click.option('-w','--webhook_url',default=None,help="[webhook] Set the url of webhook.")
@click.option('-h','--host',default=None,help="[email] SMTP server address.")
@click.option('-d','--port',default=25,help="[email] SMTP port.")
@click.option('-u','--user',default=None,help='[email] Username of sender email account.')
@click.option('-p','--passwd',default=None,help='[email] Password or token of sender email account.')
@click.option('-s','--sender',default=None,help='[email] Email address of sender.')
@click.option('-r','--receivers',default=[],help='[email] List of receivers\' email addresses.',multiple=True)
def set_config(name, config_type, webhook_url, host, port, user, passwd, sender, receivers):
	"""Create a new config."""
	thefile = f"{base_path}/config/{name}.toml"
	default = f"{base_path}/settings.toml"
	#if exists, whether overwrite
	if os.path.isfile(thefile):
		over = input(f"The config file {name}.toml already exists, do you want to overwrite it (y/n)?")
		if over == 'n':
			sys.exit(0)
	theconfig = {
		'type' : {
			'type': config_type
		},
		'sends': {
			'host': host,
			'user': user,
  			'passwd': passwd,
  			'sender': sender,
  			'port': port
		},
 		'receivers': {
			'receivers': receivers
		},
		'webhook_url': {
			"webhook_url": webhook_url
		},
		'contexts': {
			'title': '',
  			'context': ''
		},
		'default': {
			'default': ''
		}
	}
	if config_type == 'email':
		server_connect(None, host, port, user, passwd, sender)

	whe_def = input(f'Do you want to set the config {name} to default (y/others)?')
	with open(thefile, 'w') as f:
		toml.dump(theconfig, f)
	if whe_def == 'y':
		theconfig['default']['default'] = name
		with open(default, 'w') as d:
			toml.dump(theconfig, d)
	print(f"Config {name} successfully created.")
	if whe_def == 'y':
		print(f"Config {name} is set to default.")


@main.command()
@click.option('-c','--config_name', default=None, help="Check the detailed context of the config, if you want to check the default, input \'default\'.")
def list_config(config_name):
	"""List all configs or check one specific config."""
	def get_filenames_without_extension(directory_path):
		filenames = []
    
		for filename in os.listdir(directory_path):
			if os.path.isfile(os.path.join(directory_path, filename)):
				name_without_extension = os.path.splitext(filename)[0]
				filenames.append(name_without_extension)
		return filenames
	thedir = f'{base_path}/config'
	try:
		configs = get_filenames_without_extension(thedir)
	except FileNotFoundError:
		os.makedirs(f'{base_path}/config')
		configs = get_filenames_without_extension(thedir)
		
	def check_config(config_name, check_default_config):
		if not check_default_config: #name
			if not os.path.isfile(f"{thedir}/{config_name}.toml"):
				raise ConfigNotFoundError(config_name)
			with open(f'{thedir}/{config_name}.toml') as f:
				lines = f.readlines()
				for line in lines:
					print(line.strip())
		else:	
			with open(f'{base_path}/settings.toml') as f:
				lines = f.readlines()
				for line in lines:
					print(line.strip())
	
	thedefault = toml.load(f'{base_path}/settings.toml')
	current_default = thedefault['default']['default']
	if config_name is None:
		print("Configures:")
		for config in configs:
			if config == current_default:
				print(f'{config} -- default')
			else:
				print(config)
	else:
		if config_name == 'default' and 'default' in configs: #default and "default"
			check_default_config = [True if input("Fount a config named default, do you want to check the default config instead of the config named default (y/others)?\n")=='y' else False][0]
			check_config(config_name, check_default_config)
			
		elif config_name in configs: #name
			check_default_config = False
			check_config(config_name, check_default_config)

		else:	#default
			check_config(config_name, True)

@main.command()
@click.argument('name')
def set_default_config(name):
	"""Set a config to the default."""
	thedir = f'{base_path}/config'
	theconfig = f"{thedir}/{name}.toml"
	
	thedefault = toml.load(f'{base_path}/settings.toml')
	current_default = thedefault['default']['default']
	
	if os.path.isfile(theconfig) and name == current_default:
		print(f"{name} is already the default.")
	elif os.path.isfile(theconfig):
		thesetting = toml.load(theconfig)
		thesetting['default']['default'] = name
		with open(f'{base_path}/settings.toml', 'w') as f:
			toml.dump(thesetting, f)
	else:
		raise ConfigNotFoundError(name)

@main.command()
@click.argument('name')
def del_config(name):
	"""Delete a config."""
	thedefault = toml.load(f'{base_path}/settings.toml')
	current_default = thedefault['default']['default']
	whe_continue = True
	whe_default = False
	if name == current_default:
		whe_default = True
		whe_continue = [True if input(f"The config {name} is default, if you delete it, you'd better set another one as default. Do you want to continue (y/others)?\n") == 'y' else False][0]
	if whe_continue:
		os.remove(f"{base_path}/config/{name}.toml")
		if whe_default:
			os.remove(f"{base_path}/settings.toml")
			print(f"Default config has been removed, you'd better set a new default.")

if __name__=='__main__':
	main()
