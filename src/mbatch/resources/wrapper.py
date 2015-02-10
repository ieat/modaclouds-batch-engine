#!/usr/bin/env python

import os
import sys
import subprocess
import tarfile
import argparse
import json
import urllib2

def main():
    parser = argparse.ArgumentParser(description='Wrap a user task')
    parser.add_argument("--job-bundle", required=True, type=argparse.FileType("r"), help="The bundle containing the program")
    parser.add_argument("--job-input", required=False, default=None, type=argparse.FileType("r"), help="The input that should be sent to the program")
    parser.add_argument("--job-output", required=True, type=str, help="Path to the output directory")
    parser.add_argument("--job-scratch", required=True, type=str, help="Path to the scratch directory")
    parser.add_argument("--job-arguments", required=True, type=str, help="Job arguments")
    parser.add_argument("--job-uuid", required=True, type=str, help="Job UUID")
    parser.add_argument("--notification-url", required=False, type=str, help="Notification URL")
    args = parser.parse_args()

    job_info = {'job-uuid': args.job_uuid}
    expand_dir = "%s.exploded" % args.job_bundle.name
    tar = tarfile.open(fileobj=args.job_bundle)
    print >>sys.stderr, "extracting bundle to: %s" % expand_dir
    tar.extractall(expand_dir)

    bundle_entry_point = os.path.join(expand_dir, "run.sh")
    if not os.path.exists(bundle_entry_point):
        print >>sys.stderr, "Invalid bundle! Missing entrypoint"
        sys.exit(1)

    child_environment = os.environ.copy()
    if args.job_input:
        child_environment["MODACLOUDS_BATCH_INPUT"] = args.job_input.name
    child_environment["MODACLOUDS_BATCH_OUTPUT"] = args.job_output
    child_environment["MODACLOUDS_BATCH_SCRATCH_DIRECTORY"] = args.job_scratch
    command_args = "%s " % (bundle_entry_point, )
    if args.job_arguments:
        command_args += " %s" % (args.job_arguments, )

    os.chdir(expand_dir)
    child = subprocess.Popen(command_args, shell=True, env=child_environment)
    child.wait()
    if args.notification_url:
        import traceback
        job_info["retcode"] = child.returncode
        payload = json.dumps(job_info)
        try:
            req = urllib2.Request(args.notification_url, payload, {'Content-Type': 'application/json'})
            f = urllib2.urlopen(req)
            f.read()
            f.close()
        except Exception, e:
            print >>sys.stderr, "Failed to perform the HTTP call to: %s The error was: %s" % (args.notification_url,
                                                                                              str(e))
    sys.exit(child.returncode)


if __name__ == "__main__":
    main()

