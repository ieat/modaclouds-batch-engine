#!/usr/bin/env python

import os
import sys
import subprocess
import tarfile
import argparse
import pipes

def main():
    parser = argparse.ArgumentParser(description='Wrap a user task')
    parser.add_argument("--job-bundle", required=True, type=argparse.FileType("r"), help="The bundle containing the program")
    parser.add_argument("--job-input", required=False, default=None, type=argparse.FileType("r"), help="The input that should be sent to the program")
    parser.add_argument("--job-output", required=True, type=str, help="Path to the output directory")
    parser.add_argument("--job-scratch", required=True, type=str, help="Path to the scratch directory")
    parser.add_argument("--job-arguments", required=True, type=str, help="Job arguments")

    args = parser.parse_args()
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
    child = subprocess.Popen(command_args, shell=True, env=child_environment)
    child.wait()
    sys.exit(child.returncode)




if __name__ == "__main__":
    main()

