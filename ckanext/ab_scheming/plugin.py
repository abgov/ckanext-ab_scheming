import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import json
import ckanext.ab_scheming.helpers as helpers
from ckanext.ab_scheming.logic import action
from ckanext.ab_scheming.validation import (
    ab_scheming_multiple_choice
)

class Ab_SchemingPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IValidators)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ab_scheming')
        
    def dataset_facets(self, facets_dict, package_type):
        facets_dict['dataset_type'] = plugins.toolkit._('Information Type')
        facets_dict['groups'] = plugins.toolkit._('Topics')
        facets_dict['audience'] = plugins.toolkit._('Audience')
        facets_dict['pubtype'] = plugins.toolkit._('Publication Type')
        return facets_dict
        
    def before_index(self, pkg_dict):
        if 'pubtype' in pkg_dict:
            pkg_dict['pubtype'] = json.loads(pkg_dict['pubtype'])    
        return pkg_dict

    """
    ITemplateHelpers
    """
    def get_helpers(self):
        return {
            'topics_available': helpers.topics_available
        }

    """
    IAction
    """
    def get_actions(self):
        actions = dict((name, function) for name, function
                       in action.__dict__.items()
                       if callable(function))
        return actions


    """
    IValidators
    """
    def get_validators(self):
        return {'ab_scheming_multiple_choice': ab_scheming_multiple_choice}
    
    
    
