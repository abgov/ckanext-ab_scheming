import pylons.config as config
import ckan.plugins.toolkit as toolkit
from ckan.logic.action import create
from . import change_pkg_dict_for_import_deployment


def package_create(context, data_dict):
    deployment_mode = toolkit.asbool(config.get('ckan.ab_scheming.for_load_to_iddp', False))
    # need to change data_dict if import from ckanapi
    if deployment_mode:
        data_dict = change_pkg_dict_for_import_deployment(data_dict, 'create')
        if data_dict['type'] in ['publications', 'opendata']:
            context['defer_commit'] = True 
    return create.package_create(context, data_dict)


