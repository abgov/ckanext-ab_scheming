#!/usr/bin/env python
"""
Simple script to convert Vocabularies in csv
format to json format.

You can alias this at a prompt and pretty process json files
alias 'json=python -m json.tool'

"""

import sys
import csv
import json


def filename():
    return sys.argv[1]

csvfile = open( filename(), 'r')
jsonfile = open( filename() + '.json', 'w')

fieldnames = ("value","label")
reader = csv.DictReader( csvfile, fieldnames)

for row in reader:
    json.dump(row, jsonfile)
    jsonfile.write(',\n')