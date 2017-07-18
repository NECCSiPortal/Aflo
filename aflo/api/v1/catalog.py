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
import uuid

from oslo_config import cfg
from oslo_log import log as logging
import webob.exc

from aflo.api import policy
from aflo.api.v1 import controller
from aflo.catalog import manager
from aflo.common import exception
from aflo.common import utils
from aflo.common import wsgi
from aflo import i18n
from datetime import datetime

LOG = logging.getLogger(__name__)
_ = i18n._
CONF = cfg.CONF

SUPPORTED_DATE_FILTERS = ['lifetime']
SUPPORTED_FILTERS = ['catalog_id',
                     'region_id',
                     'catalog_name',
                     'lifetime']
SUPPORTED_SORT_KEYS = ('catalog_id',
                       'region_id',
                       'catalog_name',
                       'lifetime_start',
                       'lifetime_end')
SUPPORTED_SORT_DIRS = ('asc', 'desc')

CATALOG_FIELDS = (
    'catalog_id', 'region_id', 'catalog_name',
    'lifetime_start', 'lifetime_end',
    'created_at', 'updated_at', 'deleted_at', 'deleted',
    'expansion_key1', 'expansion_key2', 'expansion_key3',
    'expansion_key4', 'expansion_key5', 'expansion_text')

MODIFY_DISABLED_FIELDS = \
    ('deleted',)


def from_dict(catalog, disabled_fields=None):
    """Change catalog format.
    :param catalog: Catalog with http format.
    :param disabled_fields: modify disabled fields.
    :return: Catalog with datebase format.
    """
    if not catalog:
        return {}

    if 'expansions' in catalog:
        catalog.update(catalog.pop('expansions'))
    if 'expansions_text' in catalog:
        catalog.update(catalog.pop('expansions_text'))

    disabled_fields = \
        MODIFY_DISABLED_FIELDS + disabled_fields \
        if disabled_fields is not None and 0 < len(disabled_fields) \
        else MODIFY_DISABLED_FIELDS

    catalog = {key: val
               for key, val in catalog.items()
               if key not in disabled_fields}

    return catalog


class Controller(controller.BaseController):

    def __init__(self):
        self.policy = policy.Enforcer()
        self.manager = manager.CatalogManager()

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
            if key not in CATALOG_FIELDS:
                msg = _('Unsupported field: %s') % key
                raise webob.exc.HTTPBadRequest(msg)

        if 'region_id' in values and values['region_id'] and \
                255 < len(values['region_id']):
            params = {'name': 'region_id', 'max': 255}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'catalog_name' in values and values['catalog_name'] and \
                128 < len(values['catalog_name']):
            params = {'name': 'catalog_name', 'max': 128}
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
                4000 < len(values['expansion_text']):
            params = {'name': 'expansion_text', 'max': 4000}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

    def create(self, req, body):
        """Create one of Catalog
        :param req: The Request object coming from the wsgi layer
        :param body: The request body is a mapping of the following form::
            {'catalog':
                {'region_id': <region_id>,
                 'catalog_name': <catalog_name>,
                  ...
                },
            }
        :retval The response body is a mapping of the following form::
            {'catalog':
                {'catalog_id': <catalog_id>,
                 'region_id': <region_id>,
                 'catalog_name': <catalog_name>,
                  ...
                },
            }

        """
        self._enforce(req, 'catalog_create')

        values = from_dict(copy.deepcopy(body['catalog']))
        self._param_check(values)
        values['catalog_id'] = str(uuid.uuid4())
        catalog = self.manager.catalog_create(req.context, **values)

        return {'catalog': catalog}

    def update(self, req, body, catalog_id):
        """Update one of catalog.
            :param request: Http request.
            :param body: Request body.
            :param catalog_id: Catalog_id.
            :return Response body.
        """
        self._enforce(req, 'catalog_update')

        values = from_dict(copy.deepcopy(body['catalog']))

        del_key = ('catalog_id',
                   'created_at', 'updated_at', 'deleted_at')
        for key in del_key:
            if key in values:
                del values[key]

        self._check_catalog_id(catalog_id)
        self._param_check(values)

        values['updated_at'] = datetime.utcnow()

        catalog = self.manager.catalog_update(req.context, catalog_id,
                                              **values)

        return {'catalog': catalog}

    def show(self, req, catalog_id):
        """Return Catalog
        :param req: The Request object coming from the wsgi layer
        :param catalog_id: The Catalog id.
        :retval The response body is a mapping of the following form::
            {'catalog':
                {'catalog_id': <catalog_id>,
                 'region_id': <region_id>,
                 'catalog_name': <catalog_name>,
                 ...}
            }
        """
        self._enforce(req, 'catalog_show')

        self._check_catalog_id(catalog_id)

        try:
            rtn = self.manager.catalog_get(req.context, catalog_id)

        except exception.NotFound:
            msg = _("catalog not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(catalog=rtn)

    def _check_catalog_id(self, catalog_id):
        """Check the length of the Catalog ID"""
        msg_max_len = _('Length of %(name)s is over than %(max)d characters')

        if 64 < len(catalog_id):
            params = {'name': 'catalog_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

    def _get_filters(self, req):
        """Return a dictionary of query param filters from the request

        :param req: the Request object coming from the wsgi layer
        :retval a dict of key/value filters
        """
        filters = {}

        for param in req.params:
            if param in SUPPORTED_FILTERS:
                if param in SUPPORTED_DATE_FILTERS:
                    try:
                        datetime.strptime(req.params.get(param),
                                          '%Y-%m-%dT%H:%M:%S.%f')
                    except ValueError:
                        mesg = _("Date type of parameter "
                                 "Please specify in the format "
                                 "%s") % "%Y-%m-%dT%H:%M:%S.%f"
                        raise webob.exc.HTTPBadRequest(mesg)

                    filters[param] = \
                        utils.get_datetime_from_param(req.params.get(param))
                else:
                    filters[param] = req.params.get(param, None)

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

        msg_max_len = _('Length of %(name)s is over than %(max)d characters')
        if marker and 64 < len(marker):
            params = {'name': 'marker', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

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

    def index(self, req):
        """Return a list of catalog

        :param req: The Request object coming from the wsgi layer
        :retval The response body is a mapping of the following form::

            {'catalog':
                {'catalog_id': <catalog_id>,
                 'region_id': <region_id>,
                 'catalog_name': <catalog_name>,
                 ...
                }
            }
        """
        self._enforce(req, 'catalog_index')

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
            rtn = self.manager.catalog_list(req.context,
                                            **params)

        except exception.NotFound:
            msg = _("Catalog not found")
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(catalog=rtn)

    def delete(self, req, catalog_id):
        """Delete one of catalog.
            :param req: Http request.
            :param catalog_id: Catalog id.
        """
        self._enforce(req, 'catalog_delete')

        try:
            self.manager.catalog_delete(req.context, catalog_id)
        except exception.NotFound:
            msg = _("Catalog not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)


def create_resource():
    """Aflo resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
