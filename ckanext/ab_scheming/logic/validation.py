import ckan.lib.helpers as h
from ckan.plugins.toolkit import  Invalid, _
from ckan.lib.navl.dictization_functions import unflatten
from ckan.plugins import toolkit
import ckan.logic as logic
import ckan.lib.base as base
import re
import ckanext.ab_scheming.helpers as helpers

NotFound = logic.NotFound
abort = base.abort


def scheming_required(key, flattened_data, errors, context):
    """ 
    This validator is the standard validator for fields in 
    helpers.get_required_fields_name(). There is no need to use 
    scheming_validator 
    """
    data_dict = unflatten(flattened_data)
    if data_dict['process_state'] in helpers.get_process_state_list_not_allow_incomplete():
        if key[0] in helpers.get_required_fields_name():
            if not data_dict[key[0]]:
                raise Invalid(_('Missing value'))


def resource_required(key, flattened_data, errors, context):
    """ check resources. If empty, raise error """
    data_dict = unflatten(flattened_data)
    if not data_dict.get("id"):
        # if there is no package id, it is in creation mode
        return
    try:
        pkg_obj = toolkit.get_action("package_show")(data_dict={"id": data_dict['id']})
    except NotFound:
        abort(404, _('The dataset {id} could not be found.'
                    ).format(id=data_dict['id']))
    else:
        if data_dict['process_state'] in helpers.get_process_state_list_not_allow_incomplete():
            if not pkg_obj.get("resources") and not re.search('new_resource', toolkit.request.url):
                # we still allow adding resources in Submitted mode
                raise Invalid(_("At least one resource must be set up."))

