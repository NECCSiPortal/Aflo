# Copyright 2012 OpenStack Foundation.
# Copyright 2013 NTT corp.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import re

from oslo_log import log as logging

from aflo.common.exception import BrokerError
from aflo.common.exception import InvalidParameterValue
from aflo.common.exception import InvalidRole
from aflo.common.exception import InvalidStatus
from aflo.common import utils
from aflo.db.sqlalchemy import api as db_api
from aflo.tickettemplates import templates

LOG = logging.getLogger(__name__)

ACTION_BEFORE = 'before'
ACTION_AFTER = 'after'
MESSAGE_MAX_LENGTH = 512


class BrokerBase(object):
    """Broker Base.
    """
    def __init__(self,
                 ctxt,
                 template_contents,
                 wf_pattern_contents,
                 **values):
        """Load template contents and workflow pattern contents.
        :param ctxt: Request context.
        :param template_contents: Ticket template contents.
        :param wf_pattern_contents: Workflow Pattern contents.
        :param values: Inputted form data.
        """
        ticket_template = templates.TicketTemplate.load(template_contents)

        self.ctxt = ctxt
        self.wf_pattern = wf_pattern_contents
        self.ticket_template = ticket_template
        self.template = template_contents

        self.before_status_code = values.get('before_status_code', None)
        self.after_status_code = values.get('after_status_code', None)
        self.roles = values.get('roles', None)
        values['status'] = values.get('after_status_code', None)

    def do_exec(self, wf_action, session, **values):
        """Main Prcoess.
        :param wf_action: manupirate workflow data function.
            This function has to args
            (template, wf_pattern, session, **values).
        :param session: DB session in manupirate ticket
            and workflow data.
        :param values: Input data from form.
        """

        values['ticket_detail2'] = values.get('ticket_detail', None)
        if 'ticket_detail' in values and\
                not isinstance(values['ticket_detail'], dict):
            values['ticket_detail'] = json.loads(values['ticket_detail'])

        values['additional_data2'] = values.get('additional_data', None)
        if 'additional_data' in values and\
                not isinstance(values['additional_data'], dict):
            values['additional_data'] = json.loads(values['additional_data'])

        self._do_role_check()

        with (session).begin():
            self._do_before(self.after_status_code, session, **values)

        with (session).begin():
            ret = wf_action(self.ctxt, session,
                            self.template, self.wf_pattern, **values)

        with (session).begin():
            self._do_after(self.after_status_code, session, **values)

        return ret

    def do_exec_for_api_process(self, **values):
        """Main Prcoess for API process.
        :param values: Input data from form.
        """

        values['ticket_detail2'] = values.get('ticket_detail', None)
        if 'ticket_detail' in values and\
                not isinstance(values['ticket_detail'], dict):
            values['ticket_detail'] = json.loads(values['ticket_detail'])

        values['additional_data2'] = values.get('additional_data', None)
        if 'additional_data' in values and\
                not isinstance(values['additional_data'], dict):
            values['additional_data'] = json.loads(values['additional_data'])

        self._do_role_check()
        self._do_target_check(**values)
        self._do_validation_action(self.after_status_code, **values)

    def _do_role_check(self):
        """Validation role by now status
        """
        LOG.debug("_do_role_check Begin")

        broker_error_mes_param = \
            {'location': 'role_check',
             'cause': ''}

        invalid_role_mes_param = \
            {'before_status': '',
             'after_status': self.after_status_code,
             'roles': ''}

        try:
            if not self.wf_pattern:
                broker_error_mes_param['cause'] = \
                    "'Workflow Patterns' does not exist."
                raise BrokerError(**broker_error_mes_param)

            if not self.wf_pattern['status_list']:
                broker_error_mes_param['cause'] = \
                    "There is no item 'status_list' " \
                    "to 'Workflow Patterns'."
                raise BrokerError(**broker_error_mes_param)

            # Get status list
            status_list = self.wf_pattern['status_list']
            search_status_code = self.before_status_code \
                if self.before_status_code else "none"

            # Find status data from contents.
            status = filter(lambda status:
                            status["status_code"] == search_status_code,
                            status_list)

            if status is None:
                invalid_role_mes_param['before_status'] = search_status_code
                raise InvalidRole(**invalid_role_mes_param)

            # Get change next status contains.
            next_status_list = status[0]['next_status']

            if len(next_status_list) == 0 or\
                    next_status_list[0].get("next_status_code", None) is None:
                return

            next_status = filter(
                lambda next_status:
                next_status["next_status_code"] == self.after_status_code,
                next_status_list)

            if next_status is None:
                invalid_role_mes_param['before_status'] = search_status_code
                raise InvalidRole(**invalid_role_mes_param)

            # Get grant_role
            grant_role = next_status[0].get('grant_role', [])
            if not isinstance(grant_role, list):
                grant_role = [grant_role]

            # Valid a processing user has role in grant_role of next status
            has_role = False
            for role in grant_role:
                if role in self.roles:
                    has_role = True
                    break

            if not has_role:
                invalid_role_mes_param['before_status'] = \
                    self.before_status_code
                invalid_role_mes_param['roles'] = self.roles
                raise InvalidRole(**invalid_role_mes_param)

        finally:
            LOG.debug("_do_role_check End")

    def _do_target_check(self, **values):
        """It does check of enabling the ticket update.
        It is an error, for example, when you have already been updated.
        """
        workflow_list = db_api.workflow_list(self.ctxt, values.get('id'), 1)
        if not workflow_list:
            return

        last_wf = workflow_list[0]

        invalid_status_mess_param = \
            {'before_status': values.get('before_status_code'),
             'after_status': values.get('after_status_code')}

        if last_wf.id != values.get('last_workflow_id'):
            raise InvalidStatus(**invalid_status_mess_param)

        if 0 == len(last_wf.status_detail['next_status']):
            raise InvalidStatus(**invalid_status_mess_param)

        has_next_code = False
        for next_elm in last_wf.status_detail['next_status']:
            if not next_elm.get('next_status_code', None):
                raise InvalidStatus(**invalid_status_mess_param)

            if values.get('after_status_code') == next_elm['next_status_code']:
                has_next_code = True

        if not has_next_code:
            raise InvalidStatus(**invalid_status_mess_param)

    def _do_validation_action(self, status, **values):
        """Do validation action.
        :param status: Now status.
        :param session: DB session in manupirate ticket and workflow data.
        """
        validation = None

        action_list = self.ticket_template.get_handler_list()

        for action in action_list:
            if action['status'] == status and \
               action['timing'] == ACTION_BEFORE:
                # Get broker method
                validation = action['validation']
                break

        if validation:
            getattr(self, validation)(ctxt=self.ctxt, **values)

    def _do_broker_action(self, timing, status, session,
                          **values):
        """Do broker action.
        :param timing: Action timinig.
        :param status: Now status.
        :param session: DB session in manupirate ticket and workflow data.
        """
        broker_method = None

        action_list = self.ticket_template.get_handler_list()

        for action in action_list:
            if action['status'] == status and \
               action['timing'] == timing:
                # Get broker method
                broker_method = action.get('broker_method', None)
                break

        if broker_method:
            getattr(self, broker_method)(session=session,
                                         ctxt=self.ctxt,
                                         **values)

    def _do_before(self, status, session, **values):
        """Before Process.
        :param status: Now status.
        :param session: DB session in manupirate ticket and workflow data.
        :param values: Input data from form.
        """
        LOG.debug("_do_before Begin")

        self._do_broker_action(ACTION_BEFORE, status, session, **values)

        LOG.debug("_do_before End")

    def _do_after(self, status, session, **values):
        """After Process.
        :param status: Now status.
        :param session: DB session in manupirate ticket and workflow data.
        :param values: Input data from form.
        """
        LOG.debug("_do_after Begin")

        self._do_broker_action(ACTION_AFTER, status, session, **values)

        LOG.debug("_do_after End")

    def general_param_check(self, **values):
        """"Check Parameters.
        :param values: input data.
        """
        LOG.debug("param_check Begin")

        value = None
        parameter_list = self.ticket_template.get_parameters(
            self.before_status_code)

        for parameter in parameter_list:
            value = self._get_value(parameter, **values)
            param_type = self.ticket_template.get_parameter_type(parameter)

            if value:
                try:
                    value = str(value)
                except UnicodeEncodeError:
                    value = value.encode('utf_8')

            self._check_required(parameter, value)
            if value is None or value == '':
                continue

            if param_type == 'number':
                self._check_number(parameter, value)
            elif param_type == 'date':
                self._check_date(parameter, value)
            elif param_type == 'boolean':
                self._check_boolean(parameter, value)
            elif param_type == 'email':
                self._check_email(parameter, value)
            else:
                if self.ticket_template.get_allowed_values(parameter):
                    self._check_select(parameter, value)
                else:
                    self._check_string(parameter, value)

    def _check_number(self, parameter, value):
        if (not isinstance(value, int)) and (not value.isdigit()):
            raise InvalidParameterValue(self._create_error_meesage(
                parameter, value, 'is not number'))

        value_range = self.ticket_template.get_range(parameter)
        if value_range:
            value_min = value_range.get('min', None)
            value_max = value_range.get('max', None)

            if value_min is not None and int(value) < int(value_min):
                raise InvalidParameterValue(self._create_error_meesage(
                    parameter, value, 'is too small'))

            if value_max is not None and int(value) > int(value_max):
                raise InvalidParameterValue(self._create_error_meesage(
                    parameter, value, 'is too large'))

    def _check_date(self, parameter, value):
        if not utils.is_datetime_like(value):
            raise InvalidParameterValue(self._create_error_meesage(
                parameter, value, 'is invalid value'))

    def _check_boolean(self, parameter, value):
        if value not in ('True', 'False', True, False):
            raise InvalidParameterValue(self._create_error_meesage(
                parameter, value, 'is invalid value'))

    def _check_select(self, parameter, value):
        allowed_values = self.ticket_template.get_allowed_values(parameter)

        for allowed_value in allowed_values:
            if str(value) == str(allowed_value['value']):
                return

        raise InvalidParameterValue(self._create_error_meesage(
            parameter, value, 'is invalid value'))

    def _check_email(self, parameter, value):
        pattern = '[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}'
        if re.match(pattern, value) is None:
            raise InvalidParameterValue(self._create_error_meesage(
                parameter, value, 'is invalid email'))

    def _check_string(self, parameter, value):
        value_string = ""
        try:
            value_string = unicode(value, 'utf-8')
        except TypeError:
            value_string = value

        value_length = self.ticket_template.get_length(parameter)
        if value_length:
            value_min = value_length['min']
            value_max = value_length['max']

            if len(value_string) < int(value_min):
                raise InvalidParameterValue(self._create_error_meesage(
                    parameter, value, 'is too short'))

            if len(value_string) > int(value_max):
                raise InvalidParameterValue(self._create_error_meesage(
                    parameter, value, 'is too long'))

        pattern = self.ticket_template.get_allowed_pattern(parameter)
        if pattern:
            if re.match(pattern, value_string) is None:
                raise InvalidParameterValue(self._create_error_meesage(
                    parameter, value, 'is invalid pattern'))

    def _check_required(self, parameter, value):
        if self.ticket_template.get_required(parameter):
            if value is None or value == '':
                raise InvalidParameterValue(self._create_error_meesage(
                    parameter, value, 'is None but is required'))

    def _create_error_meesage(self, parameter, value, message):
        return {'value': value,
                'param': self.ticket_template.get_label(parameter),
                'extra_msg': message}

    def _get_value(self, parameter, **values):
        if not self.before_status_code:
            # ticket creating check
            return values['ticket_detail'].get(
                self.ticket_template.get_parameter_key(parameter), None)
        else:
            # ticket updating check
            return values['additional_data'].get(
                self.ticket_template.get_parameter_key(parameter), None)
