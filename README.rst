# MODAClouds Batch REST API

**Warning!** This is work in progress. Do not expect anything from it.

This project provides an REST API for managing the batch components of the MODAClouds Project.

It will ultimately consist from two main API's:

 - The queue management API: providing REST API's for submitting jobs, controlling jobs, etc
 - The infrastructure management API: providing the means to extend the backend cluster size according to user demands.

 
The queue management API is built on top of the [HTCondor](http://research.cs.wisc.edu/htcondor/) project.


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