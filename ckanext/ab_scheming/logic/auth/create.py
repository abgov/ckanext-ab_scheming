# encoding: utf-8

import ckan.logic.auth as logic_auth
from ckan.logic.auth import create


def member_create(context, data_dict):
    group = logic_auth.get_group_object(context, data_dict)

    if group.type == 'topics':
        return {'success': True}
    else:
        return create.member_create(context, data_dict)
    