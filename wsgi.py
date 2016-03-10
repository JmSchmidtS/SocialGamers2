# -*- coding: utf-8 -*-

import os
from server import app as application

os.environ.setdefault('ZE_CONFIG', 'config.yml')
application.load_config(os.environ['ZE_CONFIG'])
