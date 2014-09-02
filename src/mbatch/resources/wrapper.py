#!/usr/bin/env python

import sys
import time
import argparse


def main():
    parser = argparse.ArgumentParser(description='Wrap a user task')
    parser.add_argument("--job-bundle", required=True, type=argparse.FileType("r"), help="The bundle containing the program")
    parser.add_argument("--job-input", required=False, type=argparse.FileType("r"), help="The input that should be sent to the program")
    parser.add_argument("--job-output", required=True, type=str, help="Path to the output directory")
    parser.add_argument("--job-scratch", required=True, type=str, help="Path to the scratch directory")
    args = parser.parse_args()
    print args





if __name__ == "__main__":
    main()

