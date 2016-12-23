import pylons.config as config
import ckan.lib.plugins as lib_plugins
import ckan.logic as logic
import ckan.lib.dictization.model_save as model_save
import ckan.plugins as plugins
import logging
import ckanext.ab_scheming.helpers as helpers
from ckan.common import _


log = logging.getLogger(__name__)
_check_access = logic.check_access
ValidationError = logic.ValidationError
_get_action = logic.get_action
NotFound = logic.NotFound

def package_create(context, data_dict):
    '''Create a new dataset (package).

    You must be authorized to create new datasets. If you specify any groups
    for the new dataset, you must also be authorized to edit these groups.

    Plugins may change the parameters of this function depending on the value
    of the ``type`` parameter, see the
    :py:class:`~ckan.plugins.interfaces.IDatasetForm` plugin interface.

    :param name: the name of the new dataset, must be between 2 and 100
        characters long and contain only lowercase alphanumeric characters,
        ``-`` and ``_``, e.g. ``'warandpeace'``
    :type name: string
    :param title: the title of the dataset (optional, default: same as
        ``name``)
    :type title: string
    :param author: the name of the dataset's author (optional)
    :type author: string
    :param author_email: the email address of the dataset's author (optional)
    :type author_email: string
    :param maintainer: the name of the dataset's maintainer (optional)
    :type maintainer: string
    :param maintainer_email: the email address of the dataset's maintainer
        (optional)
    :type maintainer_email: string
    :param license_id: the id of the dataset's license, see
        :py:func:`~ckan.logic.action.get.license_list` for available values
        (optional)
    :type license_id: license id string
    :param notes: a description of the dataset (optional)
    :type notes: string
    :param url: a URL for the dataset's source (optional)
    :type url: string
    :param version: (optional)
    :type version: string, no longer than 100 characters
    :param state: the current state of the dataset, e.g. ``'active'`` or
        ``'deleted'``, only active datasets show up in search results and
        other lists of datasets, this parameter will be ignored if you are not
        authorized to change the state of the dataset (optional, default:
        ``'active'``)
    :type state: string
    :param type: the type of the dataset (optional),
        :py:class:`~ckan.plugins.interfaces.IDatasetForm` plugins
        associate themselves with different dataset types and provide custom
        dataset handling behaviour for these types
    :type type: string
    :param resources: the dataset's resources, see
        :py:func:`resource_create` for the format of resource dictionaries
        (optional)
    :type resources: list of resource dictionaries
    :param tags: the dataset's tags, see :py:func:`tag_create` for the format
        of tag dictionaries (optional)
    :type tags: list of tag dictionaries
    :param extras: the dataset's extras (optional), extras are arbitrary
        (key: value) metadata items that can be added to datasets, each extra
        dictionary should have keys ``'key'`` (a string), ``'value'`` (a
        string)
    :type extras: list of dataset extra dictionaries
    :param relationships_as_object: see :py:func:`package_relationship_create`
        for the format of relationship dictionaries (optional)
    :type relationships_as_object: list of relationship dictionaries
    :param relationships_as_subject: see :py:func:`package_relationship_create`
        for the format of relationship dictionaries (optional)
    :type relationships_as_subject: list of relationship dictionaries
    :param groups: the groups to which the dataset belongs (optional), each
        group dictionary should have one or more of the following keys which
        identify an existing group:
        ``'id'`` (the id of the group, string), or ``'name'`` (the name of the
        group, string),  to see which groups exist
        call :py:func:`~ckan.logic.action.get.group_list`
    :type groups: list of dictionaries
    :param owner_org: the id of the dataset's owning organization, see
        :py:func:`~ckan.logic.action.get.organization_list` or
        :py:func:`~ckan.logic.action.get.organization_list_for_user` for
        available values (optional)
    :type owner_org: string

    :returns: the newly created dataset (unless 'return_id_only' is set to True
              in the context, in which case just the dataset id will
              be returned)
    :rtype: dictionary

    This function is based on the ckan core's package_create function plus some
    logic for ckanapi import deployment. ckan.ab_scheming.deployment must be set
    in ini config file.

    '''
    model = context['model']
    user = context['user']

    # need to change data_dict if import from ckanapi
    if config.get('ckan.ab_scheming.deployment', False):
        data_dict = change_pkg_dict_for_import_deployment(data_dict)

    import pprint
    pprint.pprint(data_dict)

    if 'type' not in data_dict:
        package_plugin = lib_plugins.lookup_package_plugin()
        try:
            # use first type as default if user didn't provide type
            package_type = package_plugin.package_types()[0]
        except (AttributeError, IndexError):
            package_type = 'dataset'
            # in case a 'dataset' plugin was registered w/o fallback
            package_plugin = lib_plugins.lookup_package_plugin(package_type)
        data_dict['type'] = package_type
    else:
        package_plugin = lib_plugins.lookup_package_plugin(data_dict['type'])
    if 'schema' in context:
        schema = context['schema']
    else:
        schema = package_plugin.create_package_schema()
    _check_access('package_create', context, data_dict)
    if 'api_version' not in context:
        # check_data_dict() is deprecated. If the package_plugin has a
        # check_data_dict() we'll call it, if it doesn't have the method we'll
        # do nothing.
        check_data_dict = getattr(package_plugin, 'check_data_dict', None)
        if check_data_dict:
            try:
                check_data_dict(data_dict, schema)
            except TypeError:
                # Old plugins do not support passing the schema so we need
                # to ensure they still work
                package_plugin.check_data_dict(data_dict)
    
    #  no need of validation if in ckanapi load
    if not config.get('ckan.ab_scheming.deployment', False):
        data, errors = lib_plugins.plugin_validate(
            package_plugin, context, data_dict, schema, 'package_create')
        log.debug('package_create validate_errs=%r user=%s package=%s data=%r',
                  errors, context.get('user'),
                  data.get('name'), data_dict)
        if errors:
            model.Session.rollback()
            raise ValidationError(errors)
    else:
        data = data_dict

    rev = model.repo.new_revision()
    rev.author = user
    if 'message' in context:
        rev.message = context['message']
    else:
        rev.message = _(u'REST API: Create object %s') % data.get("name")
    if user:
        user_obj = model.User.by_name(user.decode('utf8'))
        if user_obj:
            data['creator_user_id'] = user_obj.id
    pkg = model_save.package_dict_save(data, context)
    # Needed to let extensions know the package and resources ids
    model.Session.flush()
    data['id'] = pkg.id
    if data.get('resources'):
        for index, resource in enumerate(data['resources']):
            resource['id'] = pkg.resources[index].id
    context_org_update = context.copy()
    context_org_update['ignore_auth'] = True
    context_org_update['defer_commit'] = True
    context_org_update['add_revision'] = False
    _get_action('package_owner_org_update')(context_org_update,
                                            {'id': pkg.id,
                                             'organization_id': pkg.owner_org} )
    
    
    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.create(pkg)

        item.after_create(context, data)
    
    # Make sure that a user provided schema is not used in create_views
    # and on package_show
    context.pop('schema', None)

    # Create default views for resources if necessary
    if data.get('resources'):
        logic.get_action('package_create_default_resource_views')(
            {'model': context['model'], 'user': context['user'],
             'ignore_auth': True},
            {'package': data})

    if not context.get('defer_commit'):
        model.repo.commit()

    ## need to let rest api create
    context["package"] = pkg
    ## this is added so that the rest controller can make a new location
    context["id"] = pkg.id
    log.debug('Created object %s' % pkg.name)

    return_id_only = context.get('return_id_only', False)

    output = context['id'] if return_id_only \
        else _get_action('package_show')(context, {'id': context['id']})

    return output


def change_pkg_dict_for_import_deployment(data_dict):
    if 'topic' in data_dict:
        data_dict['topics'] = data_dict['topic']
        del data_dict['topic']
    if 'extras' in data_dict:
        for e in data_dict['extras']:
            if 'topic' == e['key']:
                e['key'] = 'topics'
                break

    if 'owner_org' in data_dict:
        try:
            data_dict['organization']['name']
        except KeyError:
            raise NotFound('Could not find organization name in dataset {0}'.format(data_dict['name']))
        else:
            data_dict['owner_org'] = data_dict['organization']['name']

    all_required_fields = helpers.get_required_fields_name(data_dict['type'])
    for f in all_required_fields:
        if not exist_field_in_pkg_dict(f, data_dict):
            data_dict[f] = ''

    return data_dict


def exist_field_in_pkg_dict(field, data_dict):
    if field in data_dict:
        return True
    if 'extras' in data_dict:
        for pair in data_dict['extras']:
            if field == pair['key']:
                return True
    return False