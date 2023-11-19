#!/usr/bin/python

import argparse

from payloads import Monkey, Generator

parser = argparse.ArgumentParser(description='Test')

parser.add_argument('target_url', help='Target URL')
# parser.add_argument('-o', '--output', help='The output file', default='output.txt')
parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')

args = parser.parse_args()

print(f"target_url: {args.target_url}")

if args.verbose:
    print("Verbose mode enabled")

if not args.target_url:
    print("Target URL required")
    exit(1)

monkey = Monkey(args.target_url)

