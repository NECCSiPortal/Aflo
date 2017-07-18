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
import sys
import uuid

from oslo_config import cfg
from oslo_log import log as logging
import webob.exc

from aflo.api import policy
from aflo.api.v1 import controller
from aflo.common import exception
from aflo.common import utils
from aflo.common import wsgi
from aflo import i18n
from aflo.tickets import manager as tickets_manager
from aflo.tickettemplates import manager
from aflo.tickettemplates import templates
from aflo.workflow_patterns import manager as workflow_patterns_manager

LOG = logging.getLogger(__name__)
_ = i18n._
CONF = cfg.CONF

SUPPORTED_FILTERS = []
SUPPORTED_SORT_KEYS = ('id', 'workflow_pattern_id',
                       'created_at', 'updated_at',
                       'deleted_at', 'deleted')
SUPPORTED_SORT_DIRS = ('asc', 'desc')

TICKET_TYPE_MAX_LENGTH = 64
CONTENTS_MAX_LENGTH = 1024 * 64


class Controller(controller.BaseController):

    def __init__(self):
        self.policy = policy.Enforcer()
        self.manager = manager.TicketTemplatesManager()
        self.tickets_manager = tickets_manager.TicketsManager()
        self.workflow_patterns_manager = \
            workflow_patterns_manager.WorkflowPatternsManager()

    def _enforce(self, req, action):
        """Authorize an action against our policies"""
        try:
            self.policy.enforce(req.context, action, {})
        except exception.Forbidden:
            raise webob.exc.HTTPForbidden()

    def _get_limit(self, req):
        """Parse a limit query param into something usable."""
        try:
            limit = int(req.params.get('limit', CONF.limit_param_default))
        except ValueError:
            raise webob.exc.HTTPBadRequest(_("limit param must be an integer"))

        if limit < 0:
            raise webob.exc.HTTPBadRequest(_("limit param must be positive"))

        return min(CONF.api_limit_max, limit)

    def _get_marker(self, req):
        """Parse a marker query param into something usable."""
        try:
            marker = req.params.get('marker', None)
            if marker is None:
                return None

        except ValueError:
            raise webob.exc.\
                HTTPBadRequest(_("marker param must be an integer"))

        return marker

    def _get_force_show_deleted(self, req):
        """Parse a force_show_deleted query param into something usable."""
        force_show_deleted_str = req.params.get('force_show_deleted', 'False')
        if 'false' == force_show_deleted_str.lower():
            force_show_deleted = False
        elif 'true' == force_show_deleted_str.lower():
            force_show_deleted = True
        else:
            raise webob.exc.\
                HTTPBadRequest(_("force_show_deleted param "
                                 "must be an boolean"))

        return force_show_deleted

    def _get_enable_expansion_filters(self, req):
        """Parse a enable_expansion_filters query param
        into something usable.
        """
        enable_expansion_filters_str = req.params.get(
            'enable_expansion_filters', 'False')
        if 'true' == enable_expansion_filters_str.lower():
            enable_expansion_filters = True
        else:
            enable_expansion_filters = False

        return enable_expansion_filters

    def _get_sort_key(self, req):
        """Parse a sort key query param from the request object."""
        params = req.params.copy()
        sort_keys = []

        def _validate_sort_key(sort_key):
            if sort_key not in SUPPORTED_SORT_KEYS:
                _keys = ', '.join(SUPPORTED_SORT_KEYS)
                msg = _("Unsupported sort_key. "
                        "Acceptable values: %s") % (_keys,)
                raise webob.exc.HTTPBadRequest(explanation=msg)
            return sort_key

        while 'sort_key' in params:
            sort_keys.append(_validate_sort_key(
                params.pop('sort_key').strip()))

        return sort_keys

    def _get_sort_dir(self, req):
        """Parse a sort direction query param from the request object."""
        params = req.params.copy()
        sort_dirs = []

        def _validate_sort_dir(sort_dir):
            if sort_dir not in SUPPORTED_SORT_DIRS:
                _keys = ', '.join(SUPPORTED_SORT_DIRS)
                msg = _("Unsupported sort_dir. "
                        "Acceptable values: %s") % (_keys,)
                raise webob.exc.HTTPBadRequest(explanation=msg)
            return sort_dir

        while 'sort_dir' in params:
            sort_dirs.append(_validate_sort_dir(
                params.pop('sort_dir').strip()))

        return sort_dirs

    def _get_ticket_type(self, req):
        """Parse a ticket_type query param into something usable."""
        try:
            ticket_type = req.params.get('ticket_type', None)
            if ticket_type is None:
                return None

        except ValueError:
            raise webob.exc.\
                HTTPBadRequest(_("ticket_type param must be an integer"))

        return ticket_type

    def _get_workflow_pattern_id(self, context, wf_pattern_code):
        """Get the workflow pattern id form a workflow pattern code.
        :param context: Request context.
        :param wf_pattern_code: Workflow pattern code.
        """
        try:
            workflow_pattern = \
                self.workflow_patterns_manager.workflow_patterns_get(
                    context, None, wf_pattern_code)

            return workflow_pattern['id']

        except exception.NotFound:
            raise webob.exc.HTTPNotFound(sys.exc_info()[1])

    def index(self, req):
        """
        Return a list of TicketTemplates

        :param req: The Request object coming from the wsgi layer
        :retval The response body is a mapping of the following form::

            {'tickettemplates': [
                {'id': <id>,
                 'template_contents': '{template...}',
                 'workflow_pattern_id': <workflow_pattern_id>,
                 ...}
            ],[...],...}
        """
        self._enforce(req, 'tickettemplates_index')
        limit = self._get_limit(req)

        params = {
            'sort_key': self._get_sort_key(req),
            'sort_dir': self._get_sort_dir(req),
            'marker': self._get_marker(req),
            'force_show_deleted': self._get_force_show_deleted(req),
            'ticket_type': self._get_ticket_type(req),
        }
        if params['sort_dir']:
            dir_len = len(params['sort_dir'])
            key_len = len(params['sort_key'])

            if dir_len > 1 and dir_len != key_len:
                msg = _('Number of sort dirs does not match the number '
                        'of sort keys')
                raise webob.exc.HTTPBadRequest(explanation=msg)

        try:
            rtn = self.manager.ticket_templates_list(req.context, **params)
        except exception.NotFound:
            msg = _("Ticket templates not found")
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(tickettemplates=self._expansion_filters(req, rtn, limit))

    def show(self, req, tickettemplate_id):
        """Return a TicketTemplate
        Admin user can get a deleted data.
        :param req: The Request object coming from the wsgi layer
        :param tickettemplate_id: The TicketTemplate id.
        :retval The response body is a mapping of the following form::
            {'tickettemplate':
                {'id': <id>,
                 'template_contents': '{template...}',
                 'workflow_pattern_id': <workflow_pattern_id>,
                 ...}
            }
        """
        self._enforce(req, 'tickettemplates_show')

        try:
            rtn = self.manager.ticket_templates_get(req.context,
                                                    tickettemplate_id)

        except exception.NotFound:
            msg = _("Ticket template not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(tickettemplate=rtn)

    def create(self, req, body):
        """Create one of tickettemplate.
        :param req: The Request object coming from the wsgi layer
        :param body: The request body is a mapping of the following form::
            {'tickettemplate':
                {'template_contents': <template_contents>}
            }
        :retval The response body is a mapping of the following form::
            {"tickettemplate":
                {"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "ticket_type": "New Contract",
                "template_contents": {<json>},
                "workflow_pattern_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "created_at": "yyyy-mm-dd hh:mm:ss"
                "updated_at": ""
                "deleted_at": ""
                "deleted": "False"
                }
            }
        """
        self._enforce(req, 'tickettemplates_create')

        ticket_template = templates.TicketTemplate.load(
            body['tickettemplate'].get('template_contents', None))
        ticket_template.validate()

        template_contents = ticket_template.ticket_template_contents

        values = {
            'id': str(uuid.uuid4()),
            'template_contents': template_contents,
            'ticket_type': template_contents['ticket_type'],
            'workflow_pattern_id': self._get_workflow_pattern_id(
                req.context, template_contents['wf_pattern_code']),
        }

        tickettemplate = self.manager.ticket_templates_create(
            req.context, **values)

        # Return response.
        return dict(tickettemplate=tickettemplate)

    def delete(self, req, tickettemplate_id):
        """Delete one of the tickettemplate
        :param req: The Request object coming from the wsgi layer
        :param tickettemplate_id: The tickettemplate id.
        """
        self._enforce(req, 'tickettemplates_delete')

        # Check used data.
        filters = {
            'ticket_template_id': tickettemplate_id
        }
        tickets = self.tickets_manager.tickets_list(req.context,
                                                    filters=filters)

        if 0 < len(tickets):
            raise webob.exc.HTTPForbidden(
                _('The ticket template id is used in ticket.'))

        try:
            # Delete and Check exists data.
            self.manager.ticket_templates_delete(req.context,
                                                 tickettemplate_id)

        except exception.NotFound:
            msg = _("Ticket template not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)

    def _expansion_filters(self, req, ticket_templates, limit):
        """Filtering ticket template by expansion filters.
        :param req: The Request object coming from the wsgi layer
        :param ticket_templates: All ticket templates.
        :param limit: Maximum number of items to return.
        """
        if self._get_enable_expansion_filters(req):
            filters = CONF.ticket_template_expansion_filters.split(',')
            for filter_name in filters:
                if not filter_name:
                    continue

                try:
                    filter = utils.load_class(filter_name.strip())()
                except (ValueError, TypeError, AttributeError):
                    msg = _("Expansion filter not found")
                    raise webob.exc.HTTPNotFound(msg)

                filter.do_exec(req, ticket_templates)

        if not ticket_templates:
            return ticket_templates

        return ticket_templates[:limit]


def create_resource():
    """Aflo resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
