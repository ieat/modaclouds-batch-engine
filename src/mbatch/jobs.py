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

from flask.ext.restful import Resource, Api, reqparse, marshal_with, fields, abort
from werkzeug.datastructures import FileStorage
from flask_restful_swagger import swagger
from flask import Flask, make_response

import util

import tempfile
import uuid
import os

from mbatch.condor import submit_job, get_jobs, get_job_info, remove_job, hold_job, continue_job, get_artifact

jobs_parser = reqparse.RequestParser()
jobs_parser.add_argument('job-name', type=str, required=True)
jobs_parser.add_argument('job-arguments', type=str, required=True)
jobs_parser.add_argument('job-bundle', type=FileStorage, required=True, help="File containing the tool", location='files')
jobs_parser.add_argument('job-input', type=FileStorage)
jobs_parser.add_argument('job-notification', type=str)

work_dir = tempfile.mkdtemp(prefix="batch-engine", suffix="-work-dir")

job_fields = {
    'previous_job_status': util.CondorJobStatusString,
    'backend_job_status': util.CondorJobStatusString,
    "job_status": util.CondorJobStatusString,
    'global_job_id': fields.String,
    'cluster_id': fields.Integer,
    'id': fields.String,
    'job_run_count': fields.Integer,
    "proc_id": fields.Integer,
    "image_size": fields.Integer,
    "job_universe": util.CondorUniverseStatusString,
    "job_current_start_date": util.CondorTimeFromTimestamp,
    "job_start_date": util.CondorTimeFromTimestamp,
    "job_priority": fields.Integer,
    "exit_by_signal": fields.Boolean,
    "local_user_cpu": fields.Float,
    "exit_status": fields.Integer,
    "job_completion_date": fields.Integer
}

@swagger.model
class JobAttributes:
    resource_fields = job_fields


def get_app():
    app = Flask(__name__)
    #api = Api(app)
    api = swagger.docs(Api(app), apiVersion='0.1')
    api.add_resource(JobsList, '/jobs')
    api.add_resource(Job, '/jobs/<string:job_id>',)
    api.add_resource(JobController, '/jobs/<string:job_id>/<string:action>')
    api.add_resource(JobArtifacts, '/jobs/<string:job_id>/artifacts/<string:artifact_name>')

    return app,api

class JobsList(Resource):
    """ Job List
    """
    @swagger.operation(
        notes='List Jobs',
        nickname='get',
        parameters=[],
        responseMessages=[
            {
                "code": 200,
                "message": "Success. Listed all jobs"
            }
        ]
    )
    def get(self):
        """Enumerate all tracked jobs
        """
        jobs = [{'id': job.get('GridResource', None),
                 'backend_job_status': util.convert_status_code_to_string(job.get('JobStatus')),
                 'job_status': util.convert_status_code_to_string(job.get('FixedJobStatus')),
                 'cwd': job.get('Iwd')
                } for job in get_jobs()]
        return jobs


    @swagger.operation(
        notes='Create a new Job',
        nickname='post',
        parameters=[
            {
                "name": "job-name",
                "description": "The name of the job",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
            },
            {
                "name": "job-bundle",
                "description": "Bundle containing the job",
                "required": True,
                "allowMultiple": False,
                "dataType": "file",
                #"paramType": "body"
            },
            {
                "name": "job-arguments",
                "description": "The arguments of the job",
                "required": False,
                "allowMultiple": False,
                "dataType": "string",
            },
            {
                "name": "job-input",
                "description": "An archive (tgz) containing the files needed by the application",
                "required": True,
                "allowMultiple": False,
                "dataType": "file",
                #"paramType": "body"
            },
            {
                "name": "job-notification",
                "description": "An url that should be triggered (using POST) after the job completes",
                "required": False,
                "allowMultiple": False,
                "dataType": "string",
            }
        ],
        responseMessages = [

        ]
    )
    def post(self):
        """Submit a new job
        """
        print jobs_parser
        args = jobs_parser.parse_args()
        job_uuid = uuid.uuid4()
        job_work_dir = os.path.join(work_dir, str(job_uuid))

        job_bundle = args["job-bundle"]

        fname = args["job-bundle"].filename
        mimetype = args["job-bundle"].mimetype
        mimetype_params = args["job-bundle"].mimetype_params
        condor_job_id, job_desc = submit_job(job_uuid, job_work_dir, args["job-name"], job_bundle, job_bundle.filename,
                                             args["job-input"], args["job-notification"], args["job-arguments"])
        print args
        ret = {"job_id": str(job_uuid), "backend_id": condor_job_id}
        ret.update(job_desc)
        return ret


class Job(Resource):
    @swagger.operation(
        notes='Obtain job information',
        nickname='get',
        responseClass="JobAttributes",
        multiValuedResponse=True,
        parameters=[
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "Success."
            }
        ]
    )
    @marshal_with(job_fields)
    def get(self, job_id):
        """Retrieve job state information
        """
        job_info = get_job_info(job_id)

        if not job_info:
            abort(404, message="Job {} doesn't exist".format(job_id))

        return job_info

    @swagger.operation(
        notes='Delete Job',
        nickname='delete',
        multiValuedResponse=False,
        parameters=[
            {
                "name": "job_id",
                "description": "The id of the job to delete",
                "required": True,
                "allowMultiple": False,
                "paramType": "path",
                "dataType": "string",
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "Success."
            }
        ]
    )
    def delete(self, job_id):
        """
        Cancel a Job
        """
        job_info = get_job_info(job_id)
        if not job_info:
            abort(404, message="Job {} doesn't exist".format(job_id))
        remove_job(job_id)


class JobController(Resource):
    @swagger.operation(
        notes='Job Operations',
        nickname='put',
        parameters=[
            {
                "name": "job_id",
                "description": "The id of the job we operate on",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "Operation successful"
            }
        ]
    )
    def put(self, job_id, action):
        """Change the state of a job
        """
        job_info = get_job_info(job_id)

        if not job_info:
            abort(404, message="Job {} doesn't exist".format(job_id))

        if action == "remove":
            remove_job(job_id)
        elif action == "hold":
            hold_job(job_id)
        elif action == "continue":
            continue_job(job_id)
        else:
            abort(400, message="Action {} is not known".format(action))
        return {'result': [job_id, action]}


class JobArtifacts(Resource):
    def get(self, job_id, artifact_name):
        job_work_dir = os.path.join(work_dir, str(job_id))
        return make_response(get_artifact(job_work_dir, job_id, artifact_name))
