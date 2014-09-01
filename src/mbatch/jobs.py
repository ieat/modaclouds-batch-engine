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


from flask.ext.restful import Resource, reqparse
from werkzeug.datastructures import FileStorage


jobs_parser = reqparse.RequestParser()
jobs_parser.add_argument('job-name', type=str)
jobs_parser.add_argument('job-bundle', type=FileStorage)

class JobsList(Resource):
    def get(self):
        return {}

    def post(self):

        args = jobs_parser.parse_args()
        return args

class Job(Resource):
    pass
