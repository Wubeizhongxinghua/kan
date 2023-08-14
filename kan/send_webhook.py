import json
import toml
import requests

def send_webhook(config_file = None, webhook_url = None, title = 'The title.', context="No context here."):
	if config_file is not None:
		settings = toml.load(config_file)
		webhook_url = settings['webhook_url']['webhook_url']
		title = settings['contexts']['title']
		context = settings['contexts']['context']
	themessage = {
		"msg_type": "text",
		"content": {
			"text": f"""
{title}:
{context}
			"""
		}
	}
	headers = {
		'Content-Type': 'application/json'
	}
	response = requests.request("POST", webhook_url, headers=headers, data=json.dumps(themessage))
	print(response.text)
