import pylons.config as config
import ckan.plugins.toolkit as toolkit
from ckan.logic.action import update
from . import change_pkg_dict_for_import_deployment


def package_update(context, data_dict):
    deployment_mode = toolkit.asbool(config.get('ckan.ab_scheming.deployment', False))
    # need to change data_dict if import from ckanapi
    if deployment_mode:
        data_dict = change_pkg_dict_for_import_deployment(data_dict, 'update')
        if data_dict['type'] in ['publications', 'opendata']:
            context['defer_commit'] = True 
    return update.package_update(context, data_dict)