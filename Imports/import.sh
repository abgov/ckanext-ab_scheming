#!/bin/sh

URL=http://localhost:80
APIKEY=example-ckanapikey

#ckanapi dump datasets dataset-name --output=related_out.json -r $URL -a $APIKEY

ckanapi load organizations --input=./default/src/ckanext-ab_scheming/Vocabularies/Ministries.json  -r $URL -a $APIKEY
#ckanapi load datasets --input=/mnt/host/datasets.json      -r $URL -a $APIKEY
ckanapi load datasets --input=/mnt/host/publications.json  -r $URL -a $APIKEY 
#> /mnt/host/pubs.log 2>&1

#paster --plugin=ckan search-index rebuild_fast -c /etc/ckan/default/development.ini
