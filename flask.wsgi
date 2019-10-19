#!/usr/bin/env python

import sys

activate_this = '/var/www/api_gonsa2/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, "/var/www/api_gonsa2")

from init import app as application
