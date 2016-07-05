#!/usr/bin/env python

import csv
import json

csvfile = open('Ministries.csv', 'r')
jsonfile = open('Ministries.json', 'w')

fieldnames = ("display_name","name","title","type")
reader = csv.DictReader( csvfile, fieldnames)
for row in reader:
    json.dump(row, jsonfile)
    jsonfile.write('\n')
