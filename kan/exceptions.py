class ConfigNotFoundError(Exception):
	def __init__(self, config):
		self.config = config

	def __str__(self):
		return f"Config {self.config} not found! Use \"kan list_config\" to see valid configs."

class ConfigAbnormalError(Exception):
	def __init__(self, config):
		self.config = config
	def __str__(self):
		if config is None:
			return f"Seems your default is abnormal. You'd better reset your default config."
		else:
			return f"Seems the config {self.config} you are using is abnormal. You'd better use another one."
			
