import ckan.logic as logic
import ckan.authz as authz
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize
import pylons.config as config
import ckan.plugins.toolkit as toolkit
import sqlalchemy
from ckan.logic.action.get import package_show as _package_show
import re

_check_access = logic.check_access
_select = sqlalchemy.sql.select
_and_ = sqlalchemy.and_

def topics_list_for_user(context, data_dict):
    '''Return the all types of groups that the user has a given permission for.

    By default this returns the list of all types of groups that the currently
    authorized user can edit, i.e. the list of all types of groups that the user is an
    admin of.

    Specifically it returns the list of all types of groups that the currently
    authorized user has a given permission (for example: "manage_group") against.

    When a user becomes a member of a group in CKAN they're given a
    "capacity" (sometimes called a "role"), for example "member", "editor" or
    "admin".

    Each of these roles has certain permissions associated with it. For example
    the admin role has the "admin" permission (which means they have permission
    to do anything). The editor role has permissions like "create_dataset",
    "update_dataset" and "delete_dataset".  The member role has the "read"
    permission.

    This function returns the list of all types of groups that the authorized user
    has a given permission for. For example the list of all types of groups that the
    user is an admin of, or the list of all types of groups that the user can create
    datasets in. This takes account of when permissions cascade down an
    all types of groups hierarchy.

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
    """
    if not sysadmin:
        # for non-Sysadmins check they have the required permission

        # NB 'edit_group' doesn't exist so by default this action returns just
        # orgs with admin role
        permission = data_dict.get('permission', 'edit_group')

        roles = authz.get_roles_with_permission(permission)

        if not roles:
            return []
        user_id = authz.get_user_id_for_username(user, allow_none=True)
        if not user_id:
            return []

        q = model.Session.query(model.Member, model.Group) \
            .filter(model.Member.table_name == 'user') \
            .filter(model.Member.capacity.in_(roles)) \
            .filter(model.Member.table_id == user_id) \
            .filter(model.Member.state == 'active') \
            .join(model.Group)

        group_ids = set()
        roles_that_cascade = \
            authz.check_config_permission('roles_that_cascade_to_sub_groups')
        for member, group in q.all():
            if member.capacity in roles_that_cascade:
                group_ids |= set([
                    grp_tuple[0] for grp_tuple
                    in group.get_children_group_hierarchy(type='topics')
                    ])
            group_ids.add(group.id)

        if not group_ids:
            return []

        topics_q = topics_q.filter(model.Group.id.in_(group_ids))
    """
    orgs_list = model_dictize.group_list_dictize(topics_q.all(), context)
    for o in orgs_list:
        o['title'] = o['title'].decode('utf_8')
    return orgs_list


def package_show(context, data_dict):
    """
    Cleanup package dict when 'ckanapi dump' is called for data transfer to OGP
    """
    package_dict = _package_show(context,data_dict)
    # cleanup package dict
    ogp_dump_mode = toolkit.asbool(config.get('ckan.ab_scheming.for_dump_to_ogp', False))
    # need to change data_dict if import to OGA by ckanapi
    if ogp_dump_mode:
        package_dict = change_pkg_dict_for_dump_to_OGP(package_dict)
    return package_dict


def change_pkg_dict_for_dump_to_OGP(data_dict):
    data_dict['url'] = ''
    
    if 'topics' in data_dict:
        if not data_dict['topics']: 
            data_dict['topic'] = ['Environment']
        else:
            data_dict['topic'] = get_topic_name(data_dict['topics'])
        del data_dict['topics']

    if 'extras' in data_dict:
        for e in data_dict['extras']:
            if 'topics' == e['key']:
                e['key'] = 'topic'
                break
    
    data_dict['id'] = ''

    if 'groups' in data_dict:
        data_dict['groups'] = []

    if 'tags' in data_dict:
        for ind, t in enumerate(data_dict['tags']):
            data_dict['tags'][ind]['id'] = ''

    if 'revision_id' in data_dict:
        data_dict['revision_id'] = ''

    if not 'organization' in data_dict or not data_dict['organization']:
        data_dict['organization'] = {'name': 'servicealberta'}
    if 'organization' in data_dict:
        if data_dict['organization'].has_key('name'):
            data_dict['organization']['name'] = data_dict['organization']['name'].encode('utf-8')
        if data_dict['organization'].has_key('id'):
            data_dict['organization']['id'] = ''
        if data_dict['organization'].has_key('revision_id'):
            data_dict['organization']['revision_id'] = ''

    if not 'owner_org' in data_dict:
        data_dict['owner_org'] = ''
    if 'owner_org' in data_dict:
        try:
            data_dict['organization']['name']
        except KeyError:
            raise NotFound('Could not find organization name in dataset {0}'.format(data_dict['name']))
        else:
            data_dict['owner_org'] = data_dict['organization']['name']

    if 'resources' in data_dict:
        local_url = config.get('ckan.site_url', None)
        for r in data_dict['resources']:
            if 'classification' in r and int(r['classification']) > 1:
                continue
            if r.has_key('id'):
                r['id'] = ''
            if r.has_key('package_id'):
                r['package_id'] = ''
            if r.has_key('tracking_summary'):
                del(r['tracking_summary'])
            if r.has_key('classification'):
                del(r['classification'])
            if r.has_key('revision_id'):
                r['revision_id'] = ''
            if r.has_key('url_type') and \
               re.search(r'{0}/dataset/.*?/resource/.*?/download/.*'.format(local_url), r['url']):
                r['url_type'] = 'upload'
            if r.has_key('webstore_last_updated'):
                r['webstore_last_updated'] = ''
            if r.has_key('webstore_url'):
                r['webstore_url'] = ''

    if 'process_state' in data_dict:
        del(data_dict['private'])
    if 'reason' in data_dict:
        del(data_dict['reason'])
    
    data_dict['creator_user_id'] = ''

    if not 'creator' in data_dict or not data_dict['creator']:
            data_dict['creator'] = ['Alberta Energy Regulator']
    else:
        tmp =[]
        for c in data_dict['creator']:
            c = c.encode('utf-8')
            tmp.append(c)
        data_dict['creator'] = tmp

    if not 'contact_email' in data_dict or not data_dict['contact_email']:
        data_dict['contact_email'] = 'NA'
    if 'contact_email' in data_dict and data_dict['contact_email']:
        data_dict['email'] = data_dict['contact_email']

    if not 'contact' in data_dict or not data_dict['contact']:
        data_dict['contact'] = 'NA'

    if not 'updatefrequency' in data_dict or not data_dict['updatefrequency']:
        data_dict['updatefrequency'] = 'Once'

    if not 'sensitivity' in data_dict or not data_dict['sensitivity']:
        data_dict['sensitivity'] = 'unrestricted'

    if 'spatialcoverages' in data_dict:
        del(data_dict['spatialcoverages'])

    if 'last_process_state' in data_dict:
        del(data_dict['last_process_state'])

    if 'date_created' in data_dict and data_dict['type'] == 'publications':
        data_dict['createdate'] = data_dict['date_created']
        del(data_dict['date_created'])

    return data_dict


def get_topic_name(titles):
    if len(titles) == 0:
        return []
    if not isinstance(titles, list):
        titles = [titles]
    tmp = []
    for t in titles:
        t = t.encode('utf-8')
        try:
            t_dict = toolkit.get_action('group_show')(data_dict = {
                                                        'id': t,
                                                        'type': 'topics'
                                                    })
        except NotFound:
            raise NotFound("Topics {0} not found!".format(t))   
        
        t = t_dict['title']
        tmp.append(t)
    return tmp