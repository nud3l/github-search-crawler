import yaml
import os
from sqlalchemy import create_engine


class Config(object):
    def __init__(self):
        file_path = os.path.dirname(os.path.realpath(__file__))
        with open("{}/config.yml".format(file_path), 'r') as ymlfile:
            config = yaml.load(ymlfile)

        self.sql = config['sql']
        self.github = config['github']
        self.types = config['types']

        # create SQL connection
        self.engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
                self.sql['user'],
                self.sql['password'],
                self.sql['host'],
                self.sql['port'],
                self.sql['db']
        ))
