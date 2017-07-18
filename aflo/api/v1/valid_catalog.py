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
#

from oslo_config import cfg
from oslo_log import log as logging
import webob.exc

from aflo.api import policy
from aflo.api.v1 import controller
from aflo.common import exception
from aflo.common import wsgi
from aflo import i18n
from aflo.valid_catalog import manager
from datetime import datetime

LOG = logging.getLogger(__name__)
_ = i18n._
CONF = cfg.CONF

SUPPORTED_DATE_FILTERS = ['lifetime']
SUPPORTED_FILTERS = ['catalog_id', 'scope', 'lifetime', 'catalog_name']
SUPPORTED_SORT_DIRS = ('asc', 'desc')
SUPPORTED_SORT_KEYS = ('catalog_id', 'scope', 'catalog_name', 'price',
                       'catalog_lifetime_start', 'catalog_lifetime_end',
                       'catalog_scope_lifetime_start',
                       'catalog_scope_lifetime_end',
                       'price_lifetime_start', 'price_lifetime_end')


class Controller(controller.BaseController):
    """Controller class to obtain a valid catalog."""

    def __init__(self):
        self.policy = policy.Enforcer()
        self.manager = manager.ValidCatalogManager()

    def _enforce(self, req, action):
        """Authorize an action against our policies."""
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

    def _get_filters(self, req):
        """Return a dictionary of query param filters from the request.
        :param req: the Request object coming from the wsgi layer
        :retval a dict of key/value filters
        """
        filters = {}

        if req.context.is_admin:
            if not req.params.get('scope', None):
                msg = _('The scope is required item')
                raise webob.exc.HTTPBadRequest(msg)

        if not req.params.get('lifetime', None):
            msg = _('The lifetime is required item')
            raise webob.exc.HTTPBadRequest(msg)
        else:
            try:
                datetime.strptime(req.params.get('lifetime'),
                                  '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                raise webob.exc.HTTPBadRequest(_('lifetime must be datetime'))

        for param in req.params:
            if param in SUPPORTED_FILTERS:
                filters[param] = req.params.get(param, None)

        return filters

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

    def _get_marker(self, req):
        """Parse a marker query param into something usable."""
        catalog_marker = req.params.get('catalog_marker', None)
        catalog_scope_marker = req.params.get('catalog_scope_marker', None)
        price_marker = req.params.get('price_marker', None)
        if catalog_marker is None and catalog_scope_marker is None and\
                price_marker is None:
            return None

        if catalog_marker is None or catalog_scope_marker is None or\
                price_marker is None:
            raise webob.exc.HTTPBadRequest(
                _('Number of keys are not enough to set a marker.'))

        msg_max_len = _('Length of %(name)s is over than %(max)d characters')
        if 64 < len(catalog_marker):
            params = {'name': 'catalog_id of marker', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 64 < len(catalog_scope_marker):
            params = {'name': 'catalog_scope_id of marker', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 64 < len(price_marker):
            params = {'name': 'price_seq_no of marker', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

        return [catalog_marker, catalog_scope_marker, price_marker]

    def _get_refine_flg(self, req):
        """Parse a refine_flg query param into something usable.
        If refine_flg is True,
            get only the data of the specified tenant.
        If refine_flg is False,
            get by merging the specified tenant and default data.
        """
        refine_flg_str = req.params.get('refine_flg', 'False')
        if 'false' == refine_flg_str.lower():
            refine_flg = False
        elif 'true' == refine_flg_str.lower():
            refine_flg = True
        else:
            raise webob.exc.\
                HTTPBadRequest(_("refine_flg param "
                                 "must be an boolean"))

        return refine_flg

    def index(self, req):
        """Get a list of valid catalog.
        :param req: The Request object coming from the wsgi layer.
        :retval The response body is a mapping of the following form::
            {'valid_catalog': [
                {'catalog_id': <catalog_id>,
                 'scope': <scope>,
                 'catalog_nane': <catalog_name>,
                 ...},
            ...]
            }
        """
        self._enforce(req, 'valid_catalog_list')

        params = {
            'limit': self._get_limit(req),
            'marker': self._get_marker(req),
            'sort_key': self._get_sort_key(req),
            'sort_dir': self._get_sort_dir(req),
            'refine_flg': self._get_refine_flg(req),
            'filters': self._get_filters(req)
        }
        if params['sort_dir']:
            dir_len = len(params['sort_dir'])
            key_len = len(params['sort_key'])

            if dir_len > 1 and dir_len != key_len:
                msg = _('Number of sort dirs does not match the number '
                        'of sort keys')
                raise webob.exc.HTTPBadRequest(explanation=msg)

        try:
            rtn = self.manager.valid_catalog_list(req.context, **params)
        except exception.NotFound:
            msg = _("There is no designated marker")
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(valid_catalog=rtn)


def create_resource():
    """Aflo resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
