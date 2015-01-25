# MODAClouds Batch REST API

**Warning!** This is work in progress. Do not expect anything from it.

This project provides an REST API for managing the batch components of the MODAClouds Project.

It will ultimately consist from two main API's:

 - The queue management API: providing REST API's for submitting jobs, controlling jobs, etc
 - The infrastructure management API: providing the means to extend the backend cluster size according to user demands.

 
The queue management API is built on top of the [HTCondor](http://research.cs.wisc.edu/htcondor/) project.

## Swagger UI
The Batch Engine exposes an Swagger based UI. For accessing it connect to http://127.0.0.1:5000/api/spec.html#!/spec/post
Replace 127.0.0.1 with the corresponding IP address.

## Queue Management
### Job Submision

For job submission you need to access the `jobs` endpoint using POST and provide at least the arguments:

 1. `job-name`: The name of the job
 2. `job-bundle`: The bundle containing the application. See the bundle specification bellow
 3. `job-input`: An archive (tgz) containing the files needed by the application
 4. `job-notification`: An url that should be triggered (using POST) after the job completes.

 
Invocation:

```curl -v --data-urlencode 'job-bundle@setup.py' -X POST http://localhost:5000/jobs```

Result:

	{
		"job_id": "e0e7e44a-6cda-4e41-96e1-30d10540637f",
		"backend_id": 124
	}


The result contains bot an UUID identifying the job and the backend id for the job (for condor this would mean the `cluster_id`)

### Job Listing


For listing the running jobs you can access the `jobs` endpoint using GET.

Invocation:

```curl http://localhost:5000/jobs```

Result:

    [
        {
            "id": "724c1716-ab6d-47b8-ac8e-e9c03dbfd2b4",
            "job_status": "completed"
        },
        {
            "id": "c27d969e-9627-4a9c-9751-3180fe81abc3",
            "job_status": "completed"
        },
        {
            "id": "26efb3c3-1bd8-4328-9f22-a94950d0f006",
            "job_status": "completed"
        },
    
    ]
    
The result represents a list containing dictionary entries corresponding to jobs. The job attributes are:

 1. `id`: the UUID of the job
 2. `job_status`: the status of the job

 
### Job Information

Besides the minimal information provided by the `jobs` listing call you can use a more verbose call providing more information for a specific job.

Invokation:
`curl http://localhost:5000/jobs/<int:job_uuid>`

Example:
`curl http://localhost:5000/jobs/7db1718a-3480-4200-aac5-fdf772c4a149`

Response:

    {
        "backend_job_status": "held",
        "cluster_id": 125,
        "exit_by_signal": false,
        "exit_status": 0,
        "global_job_id": "shibox-3.local#125.0#1409747570",
        "id": "7db1718a-3480-4200-aac5-fdf772c4a149",
        "image_size": 2500000,
        "job_current_start_date": "Wed, 03 Sep 2014 15:32:56 -0000",
        "job_priority": 0,
        "job_run_count": 1,
        "job_start_date": "Wed, 03 Sep 2014 15:32:56 -0000",
        "job_status": "completed",
        "job_universe": "vanilla",
        "local_user_cpu": "0.0",
        "previous_job_status": "running",
        "proc_id": 0
    }
    

Fields of interest from the above output are:

 - `exit_status`: Represents the exit status of the user supplied application. It is independent of this middleware
 - `job_completion_date`: The date when the job was completed. Please note that this field is affected by a know bug, always returning a constant value.
 - `job_start_date`: The date when the job was initially started. The correct start date of the current run might be different.
 - `job_status`: the current status of the job. Might be:
 	- `idle`
 	- `running`
 	- `removed`
 	- `completed`
 	- `held`
 	- `submission_error` 
 - `job_universe`
 - `cluster_id`
 - `job_priority`
 - `job_run_count`

In case the provided job_id is not known to the middleware of the backend scheduler an HTTP error is returned: `404 Not Found`

### Job Control

Jobs registered with the system can be controled using a specialized call, like:

`curl http://localhost:5000/jobs/<uuid:job_id>/<string:action>`

Where the `<uuid:job_id>` placeholder represents the uuid used to identify the job.

The `<string:action>` placeholder can be any of the following:

 - `remove`: delete the job from the backend queue.
 - `hold`:  hold a job from queuing
 - `continue`: resume a suspended job
 - `release`: un-hold a `hold-ed` job
 - `suspend`: freeze the application. This only works for special applications that can be safely suspended

 
### Artifact Management

`Warning!` This part of the API might be subject of immediate change.

Invokation:

`curl http://localhost:5000/jobs/<uuid:job_id>/artifacts/<string:artifact>`

Where the `job_id` placeholder represents the uuid of the job.
The `artifact` placeholder represents valid artifacts that can be requested from the middleware, examples including:

 - `output`: an archive containing the output directory
 - `stdout`: a file containing the standard output of the application
 - `stderr`: a file containing the error output of the application
 - `_userlog`: a file containing the scheduling information. This artifact might be removed in any of the following versions. Do not use.

# Bundle Specification

Currently the bundle is expected to be an gzip compressed tar file (.tar.gz) containing at least an executable file named `run.sh`
in the root of the archive. Besides `run.sh` the archive can contain any other files.

