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

import os
import htcondor
import classad
import pipes
import codecs
import pkg_resources
from util import get_efectiv_job_status

USERLOG_FILE_NAME="user.log"
ERRLOG_FILE_NAME="err.log"
OUT_FILE_NAME="out.log"
INPUT_BASEDIR_NAME="input"
OUTPUT_DIR="output"
SCRATCH_DIR="scratch"
BUNDLE_DIR="bundle"

WRAPPER_SCRIPT=pkg_resources.resource_filename(__name__, "resources/wrapper.py")

JOB_INFO_KEYS = {
    "CurrentTime": "current_time",
    "LastJobStatus":"previous_job_status",
    "JobStatus": "backend_job_status",
    "GlobalJobId": "global_job_id",
    "ClusterId": "cluster_id",
    "GridResource": "id",
    "JobRunCount": "job_run_count",
    "ProcId": "proc_id",
    "ImageSize": "image_size",
    "JobUniverse": "job_universe",
    "JobCurrentStartDate": "job_current_start_date",
    "JobStartDate": "job_start_date",
    "JobPrio": "job_priority",
    "ExitBySignal": "exit_by_signal",
    "LocalUserCpu": "local_user_cpu",
    "ExitStatus": "exit_status",
    "CompletionDate": "job_completion_date",
    "FixedJobStatus": "job_status"
}


def get_jobs():
    schedd = htcondor.Schedd()
    jobs = schedd.query()
    for job in jobs:
        job["FixedJobStatus"] = get_efectiv_job_status(job["JobStatus"], job["OnExitHold"], job["HoldReasonCode"], job["HoldReasonSubCode"])
        yield job


def get_job_info(job_uuid):
    ret = {}
    schedd = htcondor.Schedd()
    jobs = schedd.query('GridResource=="%s"' % str(job_uuid))
    if not jobs:
        return None
    job = jobs[0]
    job["FixedJobStatus"] = get_efectiv_job_status(job["JobStatus"], job["OnExitHold"], job["HoldReasonCode"], job["HoldReasonSubCode"])
    for key in job.keys():
        if key in JOB_INFO_KEYS:
            ret[JOB_INFO_KEYS[key]] = job[key]

    #print job
    return ret


def remove_job(job_uuid):
    schedd = htcondor.Schedd()
    schedd.act(htcondor.JobAction.Remove, 'GridResource=="%s"' % str(job_uuid))


def submit_job(job_uuid, job_work_dir, job_name, job_bundle, job_bundle_name, job_input, job_notification):
    schedd = htcondor.Schedd()
    job_input_dir = os.path.join(job_work_dir, INPUT_BASEDIR_NAME)
    job_output_dir = os.path.join(job_work_dir, OUTPUT_DIR)
    job_bundle_dir = os.path.join(job_work_dir, BUNDLE_DIR)
    job_scratch_dir = os.path.join(job_work_dir, SCRATCH_DIR)
    os.makedirs(job_work_dir)
    os.makedirs(job_input_dir)
    os.makedirs(job_output_dir)
    os.makedirs(job_bundle_dir)
    os.makedirs(job_scratch_dir)
    user_log = os.path.join(job_work_dir, USERLOG_FILE_NAME)
    err_log = os.path.join(job_work_dir, ERRLOG_FILE_NAME)
    out_log = os.path.join(job_work_dir, OUT_FILE_NAME)
    input_file_name = os.path.join(job_input_dir, "input")
    job_input_directory = os.path.join(job_input_dir)
    bundle_file_name = os.path.join(job_bundle_dir, job_bundle_name)


    if isinstance(job_bundle.stream, str):
        with open(bundle_file_name, "w") as f:
            f.write(job_bundle.stream)
        f.close()
    elif isinstance(job_bundle.stream, unicode):
        charset = job_bundle.mimetype_params.get('charset', "utf-8")
        with codecs.open(bundle_file_name, "w", charset) as f:
            f.write(job_bundle.stream)
        f.close()
    else:
        job_bundle.save(bundle_file_name)



    job_arguments = "--job-bundle=%(job_bundle)s --job-output=%(job_output)s --job-scratch=%(job_scratch)s" % {
        'job_bundle': pipes.quote(bundle_file_name),
        'job_output': pipes.quote(job_output_dir),
        'job_scratch': pipes.quote(job_scratch_dir)
    }

    if job_input:
        job_arguments += "--job-input=%(job_input)s" % {'job_input': pipes.quote(input_file_name)}

    job_desc = {
        "GridResource": "%s" % job_uuid,
        "Iwd": job_work_dir,
        "Cmd": "%s" % WRAPPER_SCRIPT,
        "Arguments": job_arguments,
        "UserLog": user_log,
        "Err": err_log,
        "Out": out_log,
        "OnExitHold": "TRUE"
    }
    job_ad = classad.ClassAd(job_desc)
    condor_job_id = schedd.submit(job_ad)

    return condor_job_id, job_desc
