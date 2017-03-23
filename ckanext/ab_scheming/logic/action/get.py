import ckan.logic as logic
import ckan.authz as authz
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize
import pylons.config as config
import ckan.plugins.toolkit as toolkit
import sqlalchemy


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
