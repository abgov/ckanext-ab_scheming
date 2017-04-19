=============
ckanext-ab_scheming
=============

This extension makes use of open-data/ckanext-scheming.
This extension is being used to customize the schema, display
and editing templates.
 
* /datasets
* /opendata
* /publications
* /documents

------------
Requirements
------------
From github

* ckan/ckanext-repeating
* ckan/ckanext-scheming
* abgov/ckanext-ab_scheming

------------
Installation
------------

To install ckanext-ab_scheming:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-ab_scheming Python package into your virtual environment::

    git  clone ckanext-ab_scheming

3. Add ``ab_scheming`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

	 http://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-search-show-all-types

	 ckan.search.show_all_types = true
	 scheming.presets = ckanext.ab_scheming:presets.json
	 scheming.dataset_schemas = 
     ckanext.ab_scheming:alberta_dataset.json
     ckanext.ab_scheming:publications.json
     ckanext.ab_scheming:opendata.json


4. Restart CKAN. centos/rhel 7::

     sudo systemctl restart httpd


--------
UPDATING
--------

1. Updating ckanext-ab_scheming::

     su -s /bin/bash - ckan 
     . default/bin/activate 
     cd default/src/ckanext-ab_scheming 
     git checkout master 
     git fetch 
     git pull 
     deactivate 
     exit 
     systemctl restart httpd



---------------
Config Settings
---------------

    Setup Repeating
    git clone https://github.com/open-data/ckanext-repeating
    cd ckanext-repeating
    python setup.py develop

    Add scheming.presets to /etc/ckan/default/development.ini
    scheming.presets = ckanext.scheming:presets.json
                       ckanext.repeating:presets.json

    Add ckan.plugins 
    ckan.plugins = ... repeating ...

    Add 3 repeating field in your dataset.json file
    eg. alberta_dataset.json
    "preset": "repeating_text",
    "form_blanks": 3

------------------------
Development Installation
------------------------

To install ckanext-ab_scheming for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/abgov/ckanext-ab_scheming
    cd ckanext-ab_scheming
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.ab_scheming --cover-inclusive --cover-erase --cover-tests


---------------------
Updating Vocabularies
---------------------

To Update the Ministries as an example.

    Edit the Vocabularies/Ministries.csv
    Convert  to json
    $python Ministries_csv_json.py

    Edit Ministries.json remove 1st line    
    TODO: add to conversion script

    Import with ckanapi
    TODO: add to conversion script
    $ckanapi load organizations -I Ministries.json -p 3 -r URL -a API_KEY

Update vocabularies already in database.

    Edit the Vocabularies/update_vocabs.sql as required
    Connect to your postgres server as user authorized to run psql
    $ psql -d ckan_default -a -f $PATH/update_vocabs.sql
    Rebuild Search index
    $ paster --plugin=ckan search-index rebuild -c /etc/ckan/default/config.ini


-------------------------
Add field 'process_state'
-------------------------

This field has two choices for dropdown list. 

    The attribute 'form_restrict_choices_to' is for admin of organization and sysadmin only.
    The attribute 'choices' is for all members of organization.

----------------------------------------------------------------------
Add two flags to control ckanapi load to IDDP and ckanapi dump for OGP
----------------------------------------------------------------------

These two flags are set in ini config file.
    
    ckan.ab_scheming.for_load_to_iddp = false
    ckan.ab_scheming.for_dump_to_ogp = false

    ckan.ab_scheming.for_load_to_iddp is for ckanapi load dataset of OGP to IDDP. If need to do so, set True. If not, set False.
    ckan.ab_scheming.for_dump_to_ogp is for ckanapi dump dataset of IDDP for ckanapi load into OGP. If need to do so, set True. If not, set False.

    These two flags are also controlled in run time in url /ckan-admin/config
