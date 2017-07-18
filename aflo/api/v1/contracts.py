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

import copy
from datetime import datetime
from oslo_config import cfg
from oslo_log import log as logging
import uuid
import webob.exc

from aflo.api import policy
from aflo.api.v1 import controller
from aflo.common import exception
from aflo.common import wsgi
from aflo.contracts import manager
from aflo import i18n

LOG = logging.getLogger(__name__)
_ = i18n._
CONF = cfg.CONF

CONTRACT_FIELDS = (
    'catalog_id', 'region_id', 'project_id',
    'project_name', 'catalog_id', 'catalog_name',
    'num', 'parent_ticket_template_id',
    'ticket_template_id', 'parent_ticket_template_name',
    'ticket_template_name', 'parent_application_kinds_name',
    'application_kinds_name', 'cancel_application_id',
    'application_id', 'application_name', 'application_date',
    'parent_contract_id', 'lifetime_start', 'lifetime_end',
    'created_at', 'updated_at', 'deleted_at', 'deleted',
    'expansion_key1', 'expansion_key2', 'expansion_key3',
    'expansion_key4', 'expansion_key5', 'expansion_text')

MODIFY_DISABLED_FIELDS = \
    ('contract_id',
     'created_at', 'updated_at', 'deleted_at',
     'deleted')

SUPPORTED_SORT_KEYS = ('contract_id',
                       'project_name',
                       'catalog_name',
                       'application_id',
                       'ticket_template_name',
                       'application_name',
                       'application_date',
                       'lifetime_start',
                       'lifetime_end')

SUPPORTED_SORT_DIRS = ('asc', 'desc')


def from_dict(contract, disabled_fields=None):
    """Change contract format.
    :param contract: Contract with http format.
    :param disabled_fields: modify disabled fields.
    :return: Contract with datebase format.
    """
    if not contract:
        return {}

    if 'expansions' in contract:
        contract.update(contract.pop('expansions'))
    if 'expansions_text' in contract:
        contract.update(contract.pop('expansions_text'))

    disabled_fields = \
        MODIFY_DISABLED_FIELDS + disabled_fields \
        if disabled_fields is not None and 0 < len(disabled_fields) \
        else MODIFY_DISABLED_FIELDS

    contract = {key: val
                for key, val in contract.items()
                if key not in disabled_fields}

    return contract


class Controller(controller.BaseController):
    """Contract controller class."""

    def __init__(self):
        self.policy = policy.Enforcer()
        self.manager = manager.ContractManager()

    def _enforce(self, req, action):
        """Authorize an action against our policies"""
        try:
            self.policy.enforce(req.context, action, {})
        except exception.Forbidden:
            raise webob.exc.HTTPForbidden()

    def _param_check(self, values):
        """Parameter check.
            :param values: parameter.
        """
        msg_max_len = _('Length of %(name)s is over than %(max)d characters')

        for key in values:
            if key not in CONTRACT_FIELDS:
                msg = _('Unsupported field: %s') % key
                raise webob.exc.HTTPBadRequest(msg)

        if 'region_id' in values and values['region_id'] and \
                255 < len(values['region_id']):
            params = {'name': 'region_id', 'max': 255}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'project_id' in values and values['project_id'] and \
                64 < len(values['project_id']):
            params = {'name': 'project_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'project_name' in values and values['project_name'] and \
                64 < len(values['project_name']):
            params = {'name': 'project_name', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'catalog_id' in values and values['catalog_id'] and \
                64 < len(values['catalog_id']):
            params = {'name': 'catalog_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'catalog_name' in values and values['catalog_name'] and \
                128 < len(values['catalog_name']):
            params = {'name': 'catalog_name', 'max': 128}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'num' in values and values['num'] and \
                not isinstance(values['num'], int):
            raise webob.exc.HTTPBadRequest(_('Num must be integer'))
        if 'parent_ticket_template_id' in values and \
                values['parent_ticket_template_id'] and \
                64 < len(values['parent_ticket_template_id']):
            params = {'name': 'parent_ticket_template_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'ticket_template_id' in values and \
                values['ticket_template_id'] and \
                64 < len(values['ticket_template_id']):
            params = {'name': 'ticket_template_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'parent_ticket_template_name' in values and \
                values['parent_ticket_template_name'] and \
                65535 < len(values['parent_ticket_template_name']):
            params = {'name': 'parent_ticket_template_name', 'max': 65535}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'ticket_template_name' in values and \
                values['ticket_template_name'] and \
                65535 < len(values['ticket_template_name']):
            params = {'name': 'ticket_template_name', 'max': 65535}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'parent_application_kinds_name' in values and \
                values['parent_application_kinds_name'] and \
                65535 < len(values['parent_application_kinds_name']):
            params = {'name': 'parent_application_kinds_name', 'max': 65535}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'application_kinds_name' in values and \
                values['application_kinds_name'] and \
                65535 < len(values['application_kinds_name']):
            params = {'name': 'application_kinds_name', 'max': 65535}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'cancel_application_id' in values and \
                values['cancel_application_id'] and \
                64 < len(values['cancel_application_id']):
            params = {'name': 'cancel_application_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'application_id' in values and values['application_id'] and \
                64 < len(values['application_id']):
            params = {'name': 'application_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'application_name' in values and values['application_name'] and \
                64 < len(values['application_name']):
            params = {'name': 'application_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'application_date' in values and values['application_date']:
            try:
                datetime.strptime(values['application_date'],
                                  '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                raise webob.exc.HTTPBadRequest(_('application_date'
                                                 ' must be datetime'))
        if 'parent_contract_id' in values and \
                values['parent_contract_id'] and \
                64 < len(values['parent_contract_id']):
            params = {'name': 'parent_contract_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        dt_start = None
        dt_end = None
        if 'lifetime_start' in values and values['lifetime_start']:
            try:
                dt_start = datetime.strptime(values['lifetime_start'],
                                             '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                raise webob.exc.HTTPBadRequest(_('lifetime_start'
                                                 ' must be datetime'))
        if 'lifetime_end' in values and values['lifetime_end']:
            try:
                dt_end = datetime.strptime(values['lifetime_end'],
                                           '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                raise webob.exc.HTTPBadRequest(_('lifetime_end'
                                                 ' must be datetime'))
        if dt_start and dt_end and dt_end < dt_start:
            msg = _('Invalid lifetime period,'
                    ' begin with %(dt_start)s end with %(dt_end)s')
            params = {'dt_start': dt_start, 'dt_end': dt_end}
            raise webob.exc.HTTPBadRequest(msg % params)
        if 'expansion_key1' in values and values['expansion_key1'] and \
                255 < len(values['expansion_key1']):
            params = {'name': 'expansion_key1', 'max': 255}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'expansion_key2' in values and values['expansion_key2'] and \
                255 < len(values['expansion_key2']):
            params = {'name': 'expansion_key2', 'max': 255}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'expansion_key3' in values and values['expansion_key3'] and \
                255 < len(values['expansion_key3']):
            params = {'name': 'expansion_key3', 'max': 255}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'expansion_key4' in values and values['expansion_key4'] and \
                255 < len(values['expansion_key4']):
            params = {'name': 'expansion_key4', 'max': 255}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'expansion_key5' in values and values['expansion_key5'] and \
                255 < len(values['expansion_key5']):
            params = {'name': 'expansion_key5', 'max': 255}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'expansion_text' in values and values['expansion_text'] and \
                65535 < len(values['expansion_text']):
            params = {'name': 'expansion_text', 'max': 65535}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

    def create(self, req, body):
        """Create contract.
            :param request: Http request.
            :param body: Request body.
            :return Response body.
        """
        self._enforce(req, 'contract_create')

        values = from_dict(copy.deepcopy(body['contract']))

        self._param_check(values)

        values['contract_id'] = str(uuid.uuid4())

        contract = self.manager.contract_create(req.context, **values)

        return {'contract': contract}

    def update(self, req, body, contract_id):
        """Update one of contract.
            :param request: Http request.
            :param body: Request body.
            :param contract_id: Contract id.
            :return Response body.
        """
        self._enforce(req, 'contract_update')

        values = from_dict(copy.deepcopy(body['contract']))

        self._check_contract_id(contract_id)
        self._param_check(values)
        contract = self.manager.contract_update(req.context, contract_id,
                                                **values)

        return {'contract': contract}

    def show(self, req, contract_id):
        """Get detail contract data.
        :param req: The Request object coming from the wsgi layer
        :param contract_id: The Contract id.
        :retval The response body is a mapping of the following form::
            {'contract':
                {'contract_id': <contract_id>,
                 'region_id': <region_id>,
                 'project_id': <project_id>,
                 ...}
            }
        """
        self._enforce(req, 'contract_show')

        self._check_contract_id(contract_id)

        try:
            rtn = self.manager.contract_get(req.context, contract_id)

        except exception.NotFound:
            msg = _("Contract not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(contract=rtn)

    def _check_contract_id(self, contract_id):
        """Check the length of the Contract ID"""
        msg_max_len = _('Length of %(name)s is over than %(max)d characters')

        if contract_id and 64 < len(contract_id):
            params = {'name': 'contract_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

        return contract_id

    def _get_project_id(self, req):
        """Parse a project_id query parameter into something usable."""
        project_id = req.params.get('project_id', None)

        if not req.context.is_admin and not project_id:
            raise webob.exc.HTTPBadRequest(_("Project id is not exist."))

        return project_id

    def _get_lifetime(self, req):
        """Parse a lifetime query parameter into something usable."""
        try:
            lifetime = req.params.get('lifetime', None)
            lifetime = datetime.strptime(lifetime, '%Y-%m-%dT%H:%M:%S.%f') \
                if lifetime else None

        except ValueError:
            raise webob.exc.HTTPBadRequest(_("Lifetime must be date."))

        return lifetime

    def _get_date_in_lifetime(self, req):
        """Parse a date in lifetime query parameter into something usable."""
        try:
            lifetime = req.params.get('date_in_lifetime', None)
            lifetime = datetime.strptime(lifetime, '%Y-%m-%d') \
                if lifetime else None

        except ValueError:
            raise webob.exc.HTTPBadRequest(_("Date in Lifetime must be date."))

        return lifetime

    def _get_limit(self, req):
        """Parse a limit query parameter into something usable."""
        try:
            limit = int(req.params.get('limit', CONF.limit_param_default))
        except ValueError:
            raise webob.exc.HTTPBadRequest(_("Limit must be an integer"))

        if limit < 0:
            raise webob.exc.HTTPBadRequest(_("Limit must be positive"))

        return min(CONF.api_limit_max, limit)

    def _get_sort_key(self, req):
        """Parse a sort key query parameter from the request object."""
        sort_key = req.params.get('sort_key', None)

        sort_keys = sort_key.split(',') if sort_key else []
        for sort_key in sort_keys:
            if sort_key not in SUPPORTED_SORT_KEYS:
                _keys = ', '.join(SUPPORTED_SORT_KEYS)
                msg = _("Unsupported sort_key. Acceptable values: %s") % _keys
                raise webob.exc.HTTPBadRequest(explanation=msg)

        return sort_keys

    def _get_sort_dir(self, req):
        """Parse a sort direction query parameter from the request object."""
        sort_dir = req.params.get('sort_dir', None)
        sort_dirs = sort_dir.split(',') if sort_dir else []
        for sort_dir in sort_dirs:
            if sort_dir not in SUPPORTED_SORT_DIRS:
                _keys = ', '.join(SUPPORTED_SORT_DIRS)
                msg = _("Unsupported sort_dir. Acceptable values: %s") % _keys
                raise webob.exc.HTTPBadRequest(explanation=msg)

        return sort_dirs

    def _get_force_show_deleted(self, req):
        """Parse a force_show_deleted query parameter into something usable."""
        force_show_deleted_str = req.params.get('force_show_deleted', 'false')

        if 'false' == force_show_deleted_str.lower():
            force_show_deleted = False
        elif 'true' == force_show_deleted_str.lower():
            force_show_deleted = True
        else:
            raise webob.exc.\
                HTTPBadRequest(_("force_show_deleted parameter "
                                 "must be an boolean"))

        return force_show_deleted

    def _get_date(self, req, filter_name):

        filter_date = req.params.get(filter_name, None)

        if filter_date:
            try:
                datetime.strptime(filter_date,
                                  '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                raise webob.exc.HTTPBadRequest(_('%s must be datetime')
                                               % filter_name)

        return filter_date

    def list(self, req):
        """Get contract list.
            :param request: Http request.
            :return Contract list.
        """
        self._enforce(req, 'contract_list')

        params = {
            'project_id': self._get_project_id(req),
            'region_id': req.params.get('region_id', None),
            'project_name': req.params.get('project_name', None),
            'catalog_name': req.params.get('catalog_name', None),
            'application_id': req.params.get('application_id', None),
            'ticket_template_name': req.params.get('ticket_template_name',
                                                   None),
            'application_kinds_name': req.params.get('application_kinds_name',
                                                     None),
            'application_name': req.params.get('application_name', None),
            'parent_contract_id': req.params.get('parent_contract_id', None),
            'application_date_from': self._get_date(req,
                                                    'application_date_from'),
            'application_date_to': self._get_date(req,
                                                  'application_date_to'),
            'lifetime_start_from': self._get_date(req,
                                                  'lifetime_start_from'),
            'lifetime_start_to': self._get_date(req, 'lifetime_start_to'),
            'lifetime_end_from': self._get_date(req, 'lifetime_end_from'),
            'lifetime_end_to': self._get_date(req, 'lifetime_end_to'),
            'lifetime': self._get_lifetime(req),
            'date_in_lifetime': self._get_date_in_lifetime(req),
            'limit': self._get_limit(req),
            'marker': self._check_contract_id(req.params.get('marker', None)),
            'sort_key': self._get_sort_key(req),
            'sort_dir': self._get_sort_dir(req),
            'force_show_deleted': self._get_force_show_deleted(req)
        }

        try:
            contracts = self.manager.contract_list(req.context, **params)
        except exception.NotFound:
            msg = _("Contract not found")
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)

        return {'contract': contracts}

    def delete(self, req, contract_id):
        """Delete one of contract.
            :param request: Http request.
            :param contract_id: Contract id.
        """
        self._enforce(req, 'contract_delete')

        self._check_contract_id(contract_id)

        try:
            self.manager.contract_delete(req.context, contract_id)
        except exception.NotFound:
            msg = _("Contract not found")
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)


def create_resource():
    """Aflo resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
