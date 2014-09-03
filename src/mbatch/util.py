# -*- coding: utf-8 -*-
'''
Copyright 2014 Universitatea de Vest din Timișoara

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
@copyright: 2014 Universitatea de Vest din Timișoara
'''

import datetime
from flask.ext.restful import fields


JOB_CODES = {
    0: "unexpanded",
    1: "idle",
    2: "running",
    3: "removed",
    4: "completed",
    5: "held",
    6: "submission_error"
}

JOB_UNIVERSE_CODES = {
    0: "__min__",
    1: "standard",
    2: "pipe",
    3: "linda",
    4: "pvm",
    5: "vanilla",
    6: "pvmd",
    7: "scheduller",
    8: "mpi",
    9: "grid",
    10: "java",
    11: "parallel",
    12: "local",
    13: "__max__"
}


def convert_status_code_to_string(code):
    return JOB_CODES.get(int(code), "__unknown__")


def convert_universe_code_to_string(code):
    return JOB_UNIVERSE_CODES.get(int(code), "__unknown__")


def get_efectiv_job_status(backend_status, hold_on_exit, hold_code, hold_subcode):
    """Returns the efective status in case hold_on_exit is enabled.

    """

    if backend_status != 5:
        return backend_status
    if hold_on_exit != "TRUE":
        return backend_status
    if hold_code == 5 and hold_subcode == 0: # If held due to undefined OnExitHold evaluation
        return 4 # Return completed
    return backend_status


class CondorTimeFromClassAd(fields.DateTime):
    def format(self, value):
        dt = datetime.datetime.fromtimestamp(value.eval())
        return fields.DateTime.format(self, dt)


class CondorTimeFromTimestamp(fields.DateTime):
    def format(self, value):
        dt = datetime.datetime.fromtimestamp(value)
        return fields.DateTime.format(self, dt)


class CondorJobStatusString(fields.String):
    def format(self, value):
        return convert_status_code_to_string(value)


class CondorUniverseStatusString(fields.String):
    def format(self, value):
        return convert_universe_code_to_string(value)
