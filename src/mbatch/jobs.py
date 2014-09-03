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

from flask.ext.restful import Resource, reqparse, marshal_with, fields, abort
from werkzeug.datastructures import FileStorage

import util

import tempfile
import uuid
import os

from mbatch.condor import submit_job, get_jobs, get_job_info, remove_job, hold_job

jobs_parser = reqparse.RequestParser()
jobs_parser.add_argument('job-name', type=str)
jobs_parser.add_argument('job-bundle', type=FileStorage, required=True, help="File containing the tool")
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


class JobsList(Resource):
    def get(self):
        jobs = [{'id': job.get('GridResource', None),
                 'backend_job_status': util.convert_status_code_to_string(job.get('JobStatus')),
                 'job_status': util.convert_status_code_to_string(job.get('FixedJobStatus')),
                 'cwd': job.get('Iwd')
                } for job in get_jobs()]
        return jobs

    def post(self):
        args = jobs_parser.parse_args()
        job_uuid = uuid.uuid4()
        job_work_dir = os.path.join(work_dir, str(job_uuid))

        job_bundle = args["job-bundle"]

        fname = args["job-bundle"].filename
        mimetype = args["job-bundle"].mimetype
        mimetype_params = args["job-bundle"].mimetype_params
        condor_job_id, job_desc = submit_job(job_uuid, job_work_dir, args["job-name"], job_bundle, job_bundle.filename,
                                             args["job-input"], args["job-notification"])
        ret = {"job_id": str(job_uuid), "backend_id": condor_job_id}
        ret.update(job_desc)
        return ret


class Job(Resource):
    @marshal_with(job_fields)
    def get(self, job_id):
        job_info = get_job_info(job_id)

        if not job_info:
            abort(404, message="Job {} doesn't exist".format(job_id))

        return job_info


class JobController(Resource):
    def get(self, job_id, action):
        job_info = get_job_info(job_id)

        if not job_info:
            abort(404, message="Job {} doesn't exist".format(job_id))

        if action == "remove":
            remove_job(job_id)
        elif action == "hold":
            hold_job(job_id)
        else:
            abort(400, message="Action {} is not known".format(action))
        return {'result': [job_id, action]}
