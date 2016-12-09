import ckanext.ab_scheming.helpers as helpers
from ckan.lib.navl.dictization_functions import unflatten
from ckantoolkit import missing
import json

def scheming_validator(fn):
    """
    Decorate a validator that needs to have the scheming fields
    passed with this function. When generating navl validator lists
    the function decorated will be called passing the field
    and complete schema to produce the actual validator for each field.
    """
    fn.is_a_scheming_validator = True
    return fn

@scheming_validator
def ab_scheming_multiple_choice(field, schema):
    """
    Accept zero or more values from a list of database group topics and convert
    to a json list for storage:

    1. a list of strings, eg.:

       ["choice-a", "choice-b"]

    2. a single string for single item selection in form submissions:

       "choice-a"
    """
    choice_values = set(c['title'] for c in helpers.topics_available() )

    def validator(key, data, errors, context):
        # if there was an error before calling our validator
        # don't bother with our validation
        if errors[key]:
            return
        value = data[key]
        if value is not missing:
            if isinstance(value, basestring):
                value = [value]
            elif not isinstance(value, list):
                errors[key].append(_('expecting list of strings'))
                return
        else:
            value = []

        selected = set()
        for element in value:
            if element in choice_values:
                selected.add(element)
                continue
            errors[key].append(_('unexpected choice "%s"') % element)

        if not errors[key]:
            data[key] = json.dumps([
                c['title'] for c in helpers.topics_available() if c['title'] in selected])

            if field.get('required') and not selected:
                errors[key].append(_('Select at least one'))

    return validator
