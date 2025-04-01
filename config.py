from collections import namedtuple
import json


class Config(object):
    """Configuration module."""

    def __init__(self, config):
        self.paths = ""
        # Load config file
        with open(config, 'r') as config:
            self.config = json.load(config)
        # Extract configuration
        self.extract()

    def extract(self):
        config = self.config

        # -- Clients --
        fields = ['total', 'task', 'ratio','resouce']
        defaults = (0, None, [1,1,1], None)
        params = [config['clients'].get(field, defaults[i])
                  for i, field in enumerate(fields)]
        self.clients = namedtuple('clients', fields)(*params)

        # -- server --
        fields = ['alpha', 'beta',"select"]
        defaults = (1.4, 0.8, 'basic')
        params = [config['server'].get(field, defaults[i])
                  for i, field in enumerate(fields)]
        self.server = namedtuple('server', fields)(*params)

        # -- task --
        fields = ['block_num', 'name', 'seed', 'size']
        defaults = (5,'gpt3', 1, None )
        params = [config['task'].get(field, defaults[i])
                  for i, field in enumerate(fields)]
        self.task = namedtuple('task', fields)(*params)


    if __name__ == "__main__":
        extract();