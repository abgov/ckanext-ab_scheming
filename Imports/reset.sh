#!/bin/sh

paster --plugin=ckan db clean -c /etc/ckan/default/development.ini
paster --plugin=ckan db init -c /etc/ckan/default/development.ini

paster --plugin=ckan user add admin email=user@example.com password=XXXXXXX -c /etc/ckan/default/development.ini

paster --plugin=ckan sysadmin add admin -c /etc/ckan/default/development.ini

echo "NOTE API Key and add to import: "
paster --plugin=ckan user admin -c /etc/ckan/default/development.ini
