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
from aflo.common import exception
from aflo.common import wsgi
from aflo.goods import manager
from aflo import i18n
from datetime import datetime

LOG = logging.getLogger(__name__)
_ = i18n._
CONF = cfg.CONF

GOODS_FIELDS = (
    'goods_id', 'region_id', 'goods_name',
    'created_at', 'updated_at', 'deleted_at', 'deleted',
    'expansion_key1', 'expansion_key2', 'expansion_key3',
    'expansion_key4', 'expansion_key5', 'expansion_text')

MODIFY_DISABLED_FIELDS = \
    ('goods_id',
     'created_at', 'updated_at', 'deleted_at',
     'deleted')

SUPPORTED_SORT_KEYS = ('goods_id', 'region_id', 'goods_name')
SUPPORTED_SORT_DIRS = ('asc', 'desc')


def from_dict(goods, disabled_fields=None):
    """Change goods format.
    :param goods: Goods with http format.
    :param disabled_fields: modify disabled fields.
    :return: Goods with datebase format.
    """
    if not goods:
        return {}

    if 'expansions' in goods:
        goods.update(goods.pop('expansions'))
    if 'expansions_text' in goods:
        goods.update(goods.pop('expansions_text'))

    disabled_fields = \
        MODIFY_DISABLED_FIELDS + disabled_fields \
        if disabled_fields is not None and 0 < len(disabled_fields) \
        else MODIFY_DISABLED_FIELDS

    goods = {key: val
             for key, val in goods.items()
             if key not in disabled_fields}

    return goods


class Controller(controller.BaseController):

    def __init__(self):
        self.policy = policy.Enforcer()
        self.manager = manager.GoodsManager()

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
            if key not in GOODS_FIELDS:
                msg = _('Unsupported field: %s') % key
                raise webob.exc.HTTPBadRequest(msg)

        if 'region_id' in values and values['region_id'] and \
                255 < len(values['region_id']):
            params = {'name': 'region_id', 'max': 255}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'goods_name' in values and values['goods_name'] and \
                128 < len(values['goods_name']):
            params = {'name': 'goods_name', 'max': 128}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
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

    def _check_goods_id(self, goods_id):
        """Check the length of the Goods ID"""
        msg_max_len = _('Length of %(name)s is over than %(max)d characters')

        if goods_id and 64 < len(goods_id):
            params = {'name': 'goods_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

        return goods_id

    def _get_limit(self, req):
        """Parse a limit query param into something usable."""
        try:
            limit = int(req.params.get('limit', CONF.limit_param_default))
        except ValueError:
            raise webob.exc.HTTPBadRequest(_("limit param must be an integer"))

        if limit < 0:
            raise webob.exc.HTTPBadRequest(_("limit param must be positive"))

        return min(CONF.api_limit_max, limit)

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

    def show(self, req, goods_id):
        """Return Goods
        :param req: The Request object coming from the wsgi layer
        :param goods_id: The Goods id.
        :retval The response body is a mapping of the following form::
            {'goods':
                {'goods_id': <id>,
                 'region_id': <region_id>,
                 'goods_name': <goods_name>,
                 ...}
            }
        """
        self._enforce(req, 'goods_show')

        self._check_goods_id(goods_id)

        try:
            rtn = self.manager.goods_get(req.context, goods_id)

        except exception.NotFound:
            msg = _("goods not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(goods=rtn)

    def create(self, req, body):
        """Create one of goods
        :param req: The Request object coming from the wsgi layer
        :param body: The request body is a mapping of the following form::
             {'goods':
                {'region_id': <region_id>,
                 'goods_name': <goods_name>,
                  ...
                },
            }
        :retval The response body is a mapping of the following form::
             {'goods':
                {'goods_id': <goods_id>,
                 'region_id': <region_id>,
                 'goods_name': <goods_name>,
                  ...
                },
            }

        """
        self._enforce(req, 'goods_create')

        values = from_dict(copy.deepcopy(body['goods']))
        self._param_check(values)

        values['goods_id'] = str(uuid.uuid4())
        goods = self.manager.goods_create(req.context, **values)

        return {'goods': goods}

    def update(self, req, body, goods_id):
        """Update one of goods.
            :param req: Http request.
            :param body: Request body.
            :param goods_id: Goods_id.
            :return Response body.
        """
        self._enforce(req, 'goods_update')

        self._check_goods_id(goods_id)

        values = from_dict(copy.deepcopy(body['goods']))

        del_key = ('goods_id',
                   'created_at', 'updated_at', 'deleted_at')
        for key in del_key:
            if key in values:
                del values[key]

        self._param_check(values)

        values['updated_at'] = datetime.utcnow()

        goods = self.manager.goods_update(req.context, goods_id, **values)

        return {'goods': goods}

    def list(self, req):
        """Get goods list.
            :param req: Http request.
            :retval The response body is a mapping of the following form::
            {'goods': [
                {
                 'goods_id': <goods_id>,
                 'region_id': <region_id>,
                 'goods_name': <goods_name>,
                  ...
                },
                ...
                ]
            }
        """
        self._enforce(req, 'goods_list')

        params = {
            'limit': self._get_limit(req),
            'marker': self._get_marker(req),
            'sort_key': self._get_sort_key(req),
            'sort_dir': self._get_sort_dir(req),
            'force_show_deleted': self._get_force_show_deleted(req),
            'region_id': req.params.get('region_id', None)
        }

        if params['sort_dir']:
            dir_len = len(params['sort_dir'])
            key_len = len(params['sort_key'])

            if dir_len > 1 and dir_len != key_len:
                msg = _('Number of sort dirs does not match the number '
                        'of sort keys')
                raise webob.exc.HTTPBadRequest(explanation=msg)

        try:
            goods = self.manager.goods_list(req.context,
                                            **params)
        except exception.NotFound:
            msg = _("Goods not found")
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)

        return {'goods': goods}

    def delete(self, req, goods_id):
        """Delete one of goods.
            :param req: Http request.
            :param goods_id: Goods id.
        """
        self._enforce(req, 'goods_delete')

        try:
            self.manager.goods_delete(req.context, goods_id)
        except exception.NotFound:
            msg = _("Goods not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)


def create_resource():
    """Aflo resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
