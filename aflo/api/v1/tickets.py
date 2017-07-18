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

import datetime
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
from aflo.tickets import manager
from aflo.tickets import rpcapi
from aflo.tickettemplates import manager as templates_manager
from aflo.tickettemplates import templates

LOG = logging.getLogger(__name__)
_ = i18n._
CONF = cfg.CONF

SUPPORTED_DATE_FILTERS = ['owner_at_from', 'owner_at_to',
                          'last_confirmed_at_from', 'last_confirmed_at_to']

SUPPORTED_FILTERS = ['tenant_id', 'ticket_template_id',
                     'target_id',
                     'owner_id', 'owner_name',
                     'last_confirmer_id', 'last_confirmer_name',
                     'last_status_code',
                     'ticket_template_name',
                     'application_kinds_name']
SUPPORTED_SORT_KEYS = ('id', 'tenant_id', 'ticket_template_id',
                       'ticket_type', 'target_id',
                       'owner_id', 'owner_at',
                       'created_at', 'updated_at',
                       'deleted_at', 'deleted')
SUPPORTED_SORT_DIRS = ('asc', 'desc')


class Controller(controller.BaseController):

    def __init__(self):
        self.policy = policy.Enforcer()
        self.manager = manager.TicketsManager()
        self.templates_manager = templates_manager.TicketTemplatesManager()
        self.ticket_rpcapi = rpcapi.TicketRpcAPI()

    def _enforce(self, req, action):
        """Authorize an action against our policies"""
        try:
            self.policy.enforce(req.context, action, {})
        except exception.Forbidden:
            raise webob.exc.HTTPForbidden()

    def _get_filters(self, req):
        """Return a dictionary of query param filters from the request

        :param req: the Request object coming from the wsgi layer
        :retval a dict of key/value filters
        """
        filters = {}

        for param in req.params:
            if param in SUPPORTED_FILTERS:
                filters[param] = req.params.get(param)

            if param in SUPPORTED_DATE_FILTERS:
                if not utils.is_datetime_like(req.params.get(param)):
                    mess = _("Date type of parameter "
                             "Please specify in the format %s") % \
                        utils.SUPPORTED_DATETIME_FORMAT
                    raise webob.exc.HTTPBadRequest(mess)
                filters[param] = \
                    utils.get_datetime_from_param(req.params.get(param))

            if param == 'ticket_type':
                filters[param] = self._get_ticket_type_filter(req)
        return filters

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

    def _get_ticket_type_filter(self, req):
        """Parse a ticket_type query param from the request object."""
        params = req.params.copy()
        value = []

        while 'ticket_type' in params:
            value.append(params.pop('ticket_type').strip())

        return value

    def index(self, req):
        """
        Return a list of Tickets

        :param req: The Request object coming from the wsgi layer
        :retval The response body is a mapping of the following form::

            {'tickets': [
                {'id': <id>,
                 '_contents': '{...}',
                 'workflow_pattern_id': <workflow_pattern_id>,
                 ...}
            ],[...],...}
        """
        self._enforce(req, 'tickets_index')

        params = {
            'limit': self._get_limit(req),
            'sort_key': self._get_sort_key(req),
            'sort_dir': self._get_sort_dir(req),
            'marker': self._get_marker(req),
            'force_show_deleted': self._get_force_show_deleted(req),
            'filters': self._get_filters(req),
        }
        if params['sort_dir']:
            dir_len = len(params['sort_dir'])
            key_len = len(params['sort_key'])

            if dir_len > 1 and dir_len != key_len:
                msg = _('Number of sort dirs does not match the number '
                        'of sort keys')
                raise webob.exc.HTTPBadRequest(explanation=msg)

        try:
            rtn = self.manager.tickets_list(req.context, **params)
        except exception.NotFound:
            msg = _("Tickets not found")
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(tickets=rtn)

    def show(self, req, ticket_id):
        """Return a Ticket
        Admin user can get a deleted data.
        :param req: The Request object coming from the wsgi layer
        :param ticket_id: The Ticket id.
        :retval The response body is a mapping of the following form::
            {'ticket':
                {'id': <id>,
                 '_contents': '{...}',
                 'workflow_pattern_id': <workflow_pattern_id>,
                 ...}
            }
        """
        self._enforce(req, 'tickets_show')

        try:
            rtn = self.manager.tickets_get(req.context, ticket_id)

        except exception.NotFound:
            msg = _("Ticket not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(ticket=rtn)

    def create(self, req, body):
        """Create one of ticket
        :param req: The Request object coming from the wsgi layer
        :param body: The request body is a mapping of the following form::
             {'ticket':
                {'ticket_template_id': <ticket_template_id>,
                 'ticket_detail': <ticket_detail>,
                 'status_code' : <status_code>}
            }
        :retval The response body is a mapping of the following form::
            {
                "ticket": {
                    "id": "1",
                    "ticket_template_id": "1", ...
                },
                "workflows": []
            }
        """
        self._enforce(req, 'tickets_create')

        values = {}
        req_param = body['ticket']
        for key in req_param:
            values[key] = req_param[key]

        if 'id' not in values:
            values['id'] = None

        values['id'] = str(uuid.uuid4())
        values['tenant_id'] = req.context.tenant
        values['tenant_name'] = req.context.tenant_name
        values['owner_id'] = req.context.user
        values['owner_name'] = req.context.user_name
        values['owner_at'] = datetime.datetime.utcnow()
        values['roles'] = req.context.roles
        values['after_status_code'] = req_param['status_code']

        try:
            ticket_template = self.templates_manager.ticket_templates_get(
                req.context, values['ticket_template_id'])

        except exception.NotFound:
            raise webob.exc.HTTPNotFound(sys.exc_info()[1])

        template = templates.TicketTemplate.load(
            ticket_template.template_contents)
        wf_pattern = ticket_template.workflow_pattern

        # Load broker and validation
        broker_name = template.get_handler_class()
        broker = utils.load_class(broker_name)(
            req.context,
            template.ticket_template_contents,
            wf_pattern.wf_pattern_contents,
            **values)
        try:
            # validation
            broker.do_exec_for_api_process(**values)

        except exception.InvalidParameterValue:
            raise webob.exc.HTTPBadRequest(sys.exc_info()[1])

        except exception.InvalidRole:
            raise webob.exc.HTTPForbidden(sys.exc_info()[1])

        except exception.InvalidStatus:
            raise webob.exc.HTTPConflict(sys.exc_info()[1])

        self.ticket_rpcapi.tickets_create(req.context, **values)

        # Create response data.
        ret = {}
        ret['id'] = values['id']
        ret['ticket_template_id'] = values['ticket_template_id']
        ret['ticket_detail'] = values['ticket_detail'] \
            if hasattr(values, 'ticket_detail') else ""
        ret['owner_id'] = values['owner_id']
        ret['owner_at'] = values['owner_at']

        # Rturn response.
        return dict(ticket=ret, workflow=[])

    def update(self, req, body, ticket_id):
        """Create one of ticket
        :param req: The Request object coming from the wsgi layer
        :param body: The request body is a mapping of the following form::
            {'ticket': {
                'additional_data' : {<Such as screen input values>},
                'last_status_code': <status_code>,
                'last_workflow_id': <workflow_id>,
                'next_status_code': <status_code>
                'next_workflow_id': <workflow_id>,}
            }
        """
        self._enforce(req, 'tickets_update')

        values = {}
        req_param = body['ticket']
        for key in req_param:
            values[key] = req_param[key]

        def validate_required_param(param_name):
            if not values[param_name]:
                msg = _('%s parameter is required') % param_name
                raise webob.exc.HTTPBadRequest(explanation=msg)

        def validate_uuid_like(param_name):
            if not utils.is_uuid_like(values[param_name]):
                msg = _('Invalid %s format') % param_name
                raise webob.exc.HTTPBadRequest(explanation=msg)

        validate_required_param('last_status_code')
        validate_required_param('next_status_code')
        validate_required_param('last_workflow_id')
        validate_required_param('next_workflow_id')
        validate_uuid_like('last_workflow_id')
        validate_uuid_like('next_workflow_id')

        values['id'] = ticket_id
        values['tenant_id'] = req.context.tenant
        values['tenant_name'] = req.context.tenant_name
        values['confirmer_id'] = req.context.user
        values['confirmer_name'] = req.context.user_name
        values['confirmed_at'] = datetime.datetime.utcnow()
        values['roles'] = req.context.roles
        values['before_status_code'] = values['last_status_code']
        values['after_status_code'] = values['next_status_code']

        try:
            ticket = self.manager.tickets_get(req.context, ticket_id)
            ticket_template = self.templates_manager.ticket_templates_get(
                req.context, ticket.ticket_template_id)
        except exception.NotFound:
            raise webob.exc.HTTPNotFound(sys.exc_info()[1])

        template = templates.TicketTemplate.load(
            ticket_template.template_contents)
        wf_pattern = ticket_template.workflow_pattern

        # Load broker and validation
        broker_name = template.get_handler_class()
        broker = utils.load_class(broker_name)(
            req.context,
            template.ticket_template_contents,
            wf_pattern.wf_pattern_contents,
            **values)
        try:
            # validation
            broker.do_exec_for_api_process(**values)

        except exception.InvalidParameterValue:
            raise webob.exc.HTTPBadRequest(sys.exc_info()[1])

        except exception.InvalidRole:
            raise webob.exc.HTTPForbidden(sys.exc_info()[1])

        except exception.InvalidStatus:
            raise webob.exc.HTTPConflict(sys.exc_info()[1])

        self.ticket_rpcapi.tickets_update(req.context, ticket_id, **values)

    def delete(self, req, ticket_id):
        """Delete one of ticket
        :param req: The Request object coming from the wsgi layer
        :param ticket_id: The Ticket id.
        """
        self._enforce(req, 'tickets_delete')

        self.ticket_rpcapi.tickets_delete(req.context, ticket_id)


def create_resource():
    """Aflo resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
