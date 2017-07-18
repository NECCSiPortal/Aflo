#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#

import abc
import webob.exc

from oslo_log import log as logging

from aflo import i18n

LOG = logging.getLogger(__name__)
_ = i18n._


def _get_template_class(ticket_template_contents):
    """Load a ticket template class from contents version."""
    if ticket_template_contents is None:
        raise webob.exc.HTTPBadRequest(
            _("A template_contents is required."))

    if 'ticket_template_version' not in ticket_template_contents:
        raise webob.exc.HTTPBadRequest(
            _("Not exists ticket_template_version."))

    version = ticket_template_contents['ticket_template_version']

    if version == '2016-06-27':
        return TicketTemplate20160627
    else:
        raise webob.exc.HTTPBadRequest(
            _("Invalid ticket_template_version(%d).") % version)


class TicketTemplate(object):
    """A ticket template."""
    ticket_type_max_length = 64
    contents_max_length = 1024 * 64

    def __new__(cls, ticket_template_contents, *args, **kwargs):
        """Create a new ticket template of the appropriate class."""
        templateClass = _get_template_class(ticket_template_contents)
        return super(TicketTemplate, cls).__new__(templateClass)

    def __init__(self, ticket_template_contents):
        """Initialise the template with JSON object and set of parameters"""
        self.ticket_template_contents = ticket_template_contents

    @classmethod
    def load(cls, ticket_template_contents):
        """Load a ticket template class from contents version.
        @param ticket_template_contents: a ticket template JSON contents
        """
        return cls(ticket_template_contents)

    @abc.abstractmethod
    def validate(self):
        """Parse a ticket_template_contents query param
        into something usable.
        """
        pass


class TicketTemplate20160627(TicketTemplate):
    def validate(self):
        required_keys = {'ticket_template_name': 'name',
                         'application_kinds_name': 'name',
                         'ticket_type': 'ticket_type',
                         'wf_pattern_code': 'str',
                         'first_status_code': 'str',
                         'create': 'parameters',
                         'update': 'parameters',
                         'action': 'action'}
        if self.contents_max_length \
                < len(str(self.ticket_template_contents)):
            raise webob.exc.HTTPBadRequest(
                _("A template_contents is too long(%d).")
                % self.contents_max_length)

        error_flg = False

        # Output error log function.
        def _write_error_log(message):
            LOG.error(message)
            return True

        # Check one item in 'param' value of ticket template.
        #  Return True: valid item
        #  Return False: invalid item
        def _check_param(item):
            return isinstance(item, dict) and \
                'label' in item and isinstance(item['label'], dict) and \
                ('Default' in item['label'] or 'default' in item['label'])

        # Check one item in 'action.broker' value of ticket template.
        #  Return True: valid item
        #  Return False: invalid item
        def _action_status_check(item):
            return isinstance(item, dict) and \
                'status' in item and 'timing' in item and \
                item['timing'] in ['before', 'after'] and \
                (item['timing'] == "after" or
                 (item['timing'] == 'before' and 'validation' in item)) and \
                'broker_method' in item

        # Check format
        for key, value_type in required_keys.items():
            if key not in self.ticket_template_contents:
                error_flg = _write_error_log(
                    _("A template contents doesn't contain required key[%s].")
                    % key)
            elif self.ticket_template_contents[key] is None:
                error_flg = _write_error_log(
                    _("A template contents[%s] doesn't contain valid value.")
                    % key)
            else:
                value = self.ticket_template_contents[key]
                if value_type == 'name':
                    if (not isinstance(value, dict)) or \
                            ('Default' not in value and
                             'default' not in value):
                        error_flg = _write_error_log(
                            _("A template contents[%s] doesn't have "
                              "'Default' in dict.")
                            % key)

                elif value_type == 'str':
                    if not isinstance(value, str) and \
                            not isinstance(value, unicode):
                        error_flg = _write_error_log(
                            _("A template contents[%s] is not string.")
                            % key)

                elif value_type == 'ticket_type':
                    if not isinstance(value, str) and \
                            not isinstance(value, unicode):
                        error_flg = _write_error_log(
                            _("A template contents[%s] is not string.")
                            % key)

                    elif self.ticket_type_max_length < len(str(value)):
                        error_flg = _write_error_log(
                            _("A template contents[%(key)s] "
                              "is too long(%(max)d).")
                            % {'key': key,
                               'max': self.ticket_type_max_length})

                elif value_type == 'parameters':
                    if not isinstance(value, dict) or \
                            'parameters' not in value or \
                            0 < len(filter(lambda item:
                                           not _check_param(item),
                                           value['parameters'])):
                        error_flg = _write_error_log(
                            _("A template contents[%s] has not parameters.")
                            % key)

                elif value_type == 'action':
                    if not isinstance(value, dict):
                        error_flg = _write_error_log(
                            _("A template contents[%s] is not dict.")
                            % key)

                    elif 'broker_class' not in value or \
                            (not isinstance(value["broker_class"], str) and
                             not isinstance(value["broker_class"], unicode)):
                        error_flg = _write_error_log(
                            _("A template contents[%s] is not string.")
                            % (key + '.broker_class'))

                    elif 'broker' in value and \
                            (not isinstance(value["broker"], list) or
                             0 < len(filter(lambda item:
                                            not _action_status_check(item),
                                            value["broker"]))):
                        error_flg = _write_error_log(
                            _("A template contents[%s] is invalid value.")
                            % (key + '.broker'))

        if error_flg:
            raise webob.exc.HTTPBadRequest(
                _("Invalid template_contents. Check a logfile."))

    def get_handler_class(self):
        return self.ticket_template_contents['action']['broker_class']

    def get_handler_list(self):
        return self.ticket_template_contents['action'].get('broker', [])

    def get_parameters(self, before_status_code):
        if before_status_code is None:
            return self.ticket_template_contents.get('create', {}).get(
                'parameters', [])
        else:
            all_params = self.ticket_template_contents.get('update', {}).get(
                'parameters', [])
            return filter(lambda param:
                          self.get_parameter_status(
                              param, before_status_code) == before_status_code,
                          all_params)

    def get_parameter_type(self, parameter):
        return parameter['type']

    def get_parameter_key(self, parameter):
        return parameter['key']

    def get_type(self, parameter):
        return parameter['type']

    def get_label(self, parameter):
        label = parameter['label']
        return label.get('Default', label.get('default'))

    def get_parameter_status(self, parameter, current_status='none'):
        return parameter.get('status', current_status)

    def get_constraints(self, parameter):
        return parameter.get('constraints', {})

    def get_required(self, parameter):
        return self.get_constraints(parameter).get('required', False)

    def get_length(self, parameter):
        return self.get_constraints(parameter).get('length', None)

    def get_range(self, parameter):
        return self.get_constraints(parameter).get('range', None)

    def get_allowed_values(self, parameter):
        return self.get_constraints(parameter).get('allowed_values', None)

    def get_allowed_pattern(self, parameter):
        return self.get_constraints(parameter).get('allowed_pattern', None)
