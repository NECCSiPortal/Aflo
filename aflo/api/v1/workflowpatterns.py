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

import uuid

from oslo_config import cfg
from oslo_log import log as logging
import webob.exc

from aflo.api import policy
from aflo.api.v1 import controller
from aflo.common import exception
from aflo.common import wsgi
from aflo import i18n
from aflo.tickettemplates import manager as ticket_templates_manager
from aflo.workflow_patterns import manager as workflow_patterns_manager

LOG = logging.getLogger(__name__)
_ = i18n._
CONF = cfg.CONF

WF_PATTERN_CODE_MAX_LENGTH = 64
CONTENTS_MAX_LENGTH = 1024 * 64


class Controller(controller.BaseController):

    def __init__(self):
        self.policy = policy.Enforcer()
        self.ticket_templates_manager = \
            ticket_templates_manager.TicketTemplatesManager()
        self.workflow_patterns_manager = \
            workflow_patterns_manager.WorkflowPatternsManager()

    def _enforce(self, req, action):
        """Authorize an action against our policies"""
        try:
            self.policy.enforce(req.context, action, {})
        except exception.Forbidden:
            raise webob.exc.HTTPForbidden()

    def _get_workflow_pattern_contents(self, req_param):
        """Parse a workflow_pattern_contents query param
        into something usable.
        :param req_param: HTTP request parameters.
        """
        required_keys = ['wf_pattern_code',
                         'status_list']
        contents = req_param.get('wf_pattern_contents', None)

        if contents is None:
            raise webob.exc.HTTPBadRequest(
                _("A wf_pattern_contents is required."))
        elif CONTENTS_MAX_LENGTH < len(str(contents)):
            raise webob.exc.HTTPBadRequest(
                _("A wf_pattern_contents is too long(%d).")
                % CONTENTS_MAX_LENGTH)

        error_flg = False

        # Output error log function.
        def _write_error_log(message):
            LOG.error(message)
            return True

        # Check one item in 'status_list' value of workflow pattern.
        #  Return True: valid item
        #  Return False: invalid item
        def _check_status(item):
            status_required_keys = ['status_code',
                                    'status_name',
                                    'next_status']
            if not isinstance(item, dict):
                return False

            for key in status_required_keys:
                if key not in item:
                    return False

            if not isinstance(item['status_code'], str) and \
                    not isinstance(item['status_code'], unicode):
                return False

            if not isinstance(item['status_name'], dict) or \
                    'Default' not in item['status_name']:
                return False

            if not isinstance(item['next_status'], list):
                return False

            return True

        # Check format
        for key in required_keys:
            if key not in contents:
                error_flg = _write_error_log(
                    _("A workflow pattern contents doesn't "
                      "contain required key[%s].")
                    % key)
            elif contents[key] is None:
                error_flg = _write_error_log(
                    _("A workflow pattern contents[%s] doesn't "
                      "contain valid value.")
                    % key)
            else:
                value = contents[key]
                if key == 'wf_pattern_code':
                    if not isinstance(value, str) and \
                            not isinstance(value, unicode):
                        error_flg = _write_error_log(
                            _("A workflow pattern contents[%s] is "
                              "not string.")
                            % key)

                    elif WF_PATTERN_CODE_MAX_LENGTH < len(str(value)):
                        error_flg = _write_error_log(
                            _("A workflow pattern contents[%(key)s] "
                              "is too long(%(max)d).")
                            % {'key': key, 'max': WF_PATTERN_CODE_MAX_LENGTH})

                elif key == 'status_list':
                    if not isinstance(value, list) or \
                            len(value) <= 0:
                        error_flg = _write_error_log(
                            _("A workflow pattern contents[%s] is not "
                              "list or nothing.")
                            % key)

                    elif 0 < len(filter(lambda item:
                                        not _check_status(item),
                                        value)):
                        error_flg = _write_error_log(
                            _("A workflow pattern contents[%s] doesn't have "
                              "valid status")
                            % key)

                    elif len(filter(lambda item:
                                    item['status_code'] == 'none',
                                    value)) <= 0:
                        error_flg = _write_error_log(
                            _("A workflow pattern contents[%s] doesn't have "
                              "start status(none)")
                            % key)

        if error_flg:
            raise webob.exc.HTTPBadRequest(
                _("Invalid workflow pattern contents. Check a logfile."))

        return contents

    def _check_not_exists_workflow_pattern_code(self,
                                                context,
                                                wf_pattern_code):
        """Get the workflow pattern data form a workflow pattern code.
        It is normal by this method that it becomes 'NotFound'.
        :param context: Request context.
        :param wf_pattern_code: Workflow pattern code.
        """
        try:
            self.workflow_patterns_manager.workflow_patterns_get(
                context, None, wf_pattern_code)

            raise webob.exc.HTTPForbidden(
                _("Workflow pattern code has been already "
                  "registered with DB "))

        except exception.NotFound:
            pass

    def create(self, req, body):
        """Create one of workflow pattern.
        :param req: The Request object coming from the wsgi layer
        :param body: The request body is a mapping of the following form::
            {'workflowpattern':
                {'wf_pattern_contents': <wf_pattern_contents>}
            }
        :retval The response body is a mapping of the following form::
            {"workflowpattern":
                {"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "code": "work flow pattern code",
                "wf_pattern_contents": {<json>},
                "created_at": "yyyy-mm-dd hh:mm:ss"
                "updated_at": ""
                "deleted_at": ""
                "deleted": "False"
                }
            }
        """
        self._enforce(req, 'workflowpatterns_create')

        req_param = body['workflowpattern']
        wf_pattern_contents = self._get_workflow_pattern_contents(req_param)

        values = {
            'id': str(uuid.uuid4()),
            'code': wf_pattern_contents['wf_pattern_code'],
            'wf_pattern_contents': wf_pattern_contents
        }

        self._check_not_exists_workflow_pattern_code(
            req.context,
            wf_pattern_contents['wf_pattern_code'])

        workflowpattern = self.workflow_patterns_manager.\
            workflow_patterns_create(req.context, **values)

        # Return response.
        return dict(workflowpattern=workflowpattern)

    def delete(self, req, workflowpattern_id):
        """Delete one of the workflow pattern
        :param req: The Request object coming from the wsgi layer
        :param workflowpattern_id: The workflow pattern id.
        """
        self._enforce(req, 'workflowpatterns_delete')

        # Check used data.
        filters = {
            'workflow_pattern_id': workflowpattern_id
        }
        tickettemplates = \
            self.ticket_templates_manager.ticket_templates_list(
                req.context,
                filters=filters)

        if 0 < len(tickettemplates):
            raise webob.exc.HTTPForbidden(
                _('The workflow pattern id is used in a ticket template.'))

        try:
            # Delete and Check exists data.
            self.workflow_patterns_manager.workflow_patterns_delete(
                req.context,
                workflowpattern_id)

        except exception.NotFound:
            msg = _("Workflow pattern not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)


def create_resource():
    """Aflo resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
