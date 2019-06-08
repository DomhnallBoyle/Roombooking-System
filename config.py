import os


class Config(object):
	"""
	common configurations
	"""
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USE_SSL = False
	MAIL_USERNAME = 'csc3045cs2test@gmail.com'
	MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


class DevelopmentConfig(Config):
	"""
	Development configurations
	"""
	DEBUG = True


class ProductionConfig(Config):
	DEBUG = False


class TestConfig(Config):
	TESTING = True
	DEBUG = True


app_config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig,
	'testing': TestConfig
}

# administrator list
ADMINS = ['domhnallboyle@gmail.com', 'ciaran.duncan@gmail.com']
