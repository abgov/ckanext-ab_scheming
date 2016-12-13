# -*- coding: utf-8 -*-

import ckan.logic as logic
import ckan.authz as authz
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize

_check_access = logic.check_access

def topics_list_for_user(context, data_dict):
    '''Return the all types of groups that the user has a given permission for.

    By default this returns the list of all types of groups that the currently
    authorized user can edit, i.e. the list of all types of groups that the user is an
    admin of.

    Specifically it returns the list of all types of groups that the currently
    authorized user has a given create permission (for example: "manage_group") 
    against.

    :param permission: the permission the user has against the
        returned organizations, for example ``"read"`` or ``"create_dataset"``
        (optional, default: ``"edit_group"``)
    :type permission: string

    :returns: list of all types of groups that the user has the given permission for
    :rtype: list of dicts

    '''
    model = context['model']
    user = context['user']

    _check_access('organization_list_for_user', context, data_dict)
    sysadmin = authz.is_sysadmin(user)

    topics_q = model.Session.query(model.Group) \
        .filter(model.Group.type == "topics") \
        .filter(model.Group.state == 'active')
    
    orgs_list = model_dictize.group_list_dictize(topics_q.all(), context)
    for o in orgs_list:
        o['title'] = o['title'].decode('utf_8')
    return orgs_list
