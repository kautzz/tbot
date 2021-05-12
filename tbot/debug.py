import logging as log
import argparse

# Command Line Options
parser = argparse.ArgumentParser(description='tbot')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()
if args.verbose:
    log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
