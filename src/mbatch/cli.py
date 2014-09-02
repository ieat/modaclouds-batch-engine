# -*- coding: utf-8 -*-
'''
Copyright 2014 Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@info.uvt.ro>
@contact: marian@info.uvt.ro
@copyright: 2014 Institute eAustria
'''

import sys

from flask import Flask
from flask.ext.restful import Api
from jobs import JobsList, Job

def main():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(JobsList, '/jobs')
    api.add_resource(Job, '/jobs/<string:job_id>')
    app.run(debug=True)
