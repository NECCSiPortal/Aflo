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
from aflo.catalog_contents import manager
from aflo.common import exception
from aflo.common import wsgi
from aflo import i18n

LOG = logging.getLogger(__name__)
_ = i18n._
CONF = cfg.CONF

CONTENTS_FIELDS = (
    'catalog_id', 'seq_no', 'goods_id', 'goods_num',
    'created_at', 'updated_at', 'deleted_at', 'deleted',
    'expansion_key1', 'expansion_key2', 'expansion_key3',
    'expansion_key4', 'expansion_key5', 'expansion_text')

MODIFY_DISABLED_FIELDS = \
    ('contract_id', 'seq_no',
     'created_at', 'updated_at', 'deleted_at',
     'deleted')
SUPPORTED_SORT_KEYS = ('goods_id',
                       'goods_num')

SUPPORTED_SORT_DIRS = ('asc', 'desc')


def from_dict(catalog_contents, disabled_fields=None):
    """Change catalog contents format.
    :param catalog_contents: Catalog contents with http format.
    :param disabled_fields: modify disabled fields.
    :return: Catalog contents with datebase format.
    """
    if not catalog_contents:
        return {}

    if 'expansions' in catalog_contents:
        catalog_contents.update(catalog_contents.pop('expansions'))
    if 'expansions_text' in catalog_contents:
        catalog_contents.update(catalog_contents.pop('expansions_text'))

    disabled_fields = \
        MODIFY_DISABLED_FIELDS + disabled_fields \
        if disabled_fields is not None and 0 < len(disabled_fields) \
        else MODIFY_DISABLED_FIELDS

    catalog_contents = {key: val
                        for key, val in catalog_contents.items()
                        if key not in disabled_fields}

    return catalog_contents


class Controller(controller.BaseController):
    """CatalogContents controller class."""

    def __init__(self):
        self.policy = policy.Enforcer()
        self.manager = manager.CatalogContentsManager()

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
            if key not in CONTENTS_FIELDS:
                msg = _('Unsupported field: %s') % key
                raise webob.exc.HTTPBadRequest(msg)

        if 'goods_id' in values and values['goods_id'] and \
                64 < len(values['goods_id']):
            params = {'name': 'goods_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)
        if 'goods_num' in values and values['goods_num']:
            if not isinstance(values['goods_num'], int):
                raise webob.exc.HTTPBadRequest(_('goods_num must be number'))
            if 4 < len(str(values['goods_num'])):
                params = {'name': 'goods_num', 'max': 4}
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

    def create(self, req, body, catalog_id):
        """Create one of catalog contents
        :param req: The Request object coming from the wsgi layer
        :param body: The request body is a mapping of the following form::
            {'catalog_contents':
                {'goods_id': <goods_id>,
                 'goods_num': <goods_num>,
                  ...
                }
            }
        :retval The response body is a mapping of the following form::
             {'catalog_contents':
                {'catalog_id': <catalog_id>,
                 'seq_no': <seq_no>,
                 'goods_id': <goods_id>,
                 'goods_num': <goods_num>,
                  ...
                },
            }

        """
        self._enforce(req, 'catalog_contents_create')

        self._check_catalog_id(catalog_id)

        values = from_dict(copy.deepcopy(body['catalog_contents']))
        self._param_check(values)

        values['catalog_id'] = catalog_id
        values['seq_no'] = str(uuid.uuid4())

        catalog_contents = self.manager.\
            catalog_contents_create(req.context, **values)

        return {'catalog_contents': catalog_contents}

    def _check_catalog_id(self, catalog_id):
        """Check the length of the catalog contents ID"""
        msg_max_len = _('Length of %(name)s is over than %(max)d characters')

        if catalog_id and 64 < len(catalog_id):
            params = {'name': 'catalog_id', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

        return catalog_id

    def _check_seq_no(self, seq_no):
        """Check the length of the Contract ID"""
        msg_max_len = _('Length of %(name)s is over than %(max)d characters')

        if seq_no and 64 < len(seq_no):
            params = {'name': 'seq_no', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

        return seq_no

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

    def _get_marker(self, req):
        """Parse a marker query param into something usable."""
        try:
            marker = req.params.get('marker', None)
            if marker is None:
                return None

        except ValueError:
            raise webob.exc.\
                HTTPBadRequest(_("marker param must be UUID"))

        msg_max_len = _('Length of %(name)s is over than %(max)d characters')
        if marker and 64 < len(marker):
            params = {'name': 'marker', 'max': 64}
            raise webob.exc.HTTPBadRequest(msg_max_len % params)

        return marker

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

    def list(self, req, catalog_id):
        """Get catalog_contents list.
            :param request: Http request.
            :param catalog_id: catalog_id of catalog_contents.
            :return CatalogContents list.
        """
        self._enforce(req, 'catalog_contents_list')

        self._check_catalog_id(catalog_id)

        params = {
            'limit': self._get_limit(req),
            'marker': self._get_marker(req),
            'sort_key': self._get_sort_key(req),
            'sort_dir': self._get_sort_dir(req),
            'force_show_deleted': self._get_force_show_deleted(req)
        }

        try:
            catalog_contents = self.manager.catalog_contents_list(req.context,
                                                                  catalog_id,
                                                                  **params)
        except exception.NotFound:
            msg = _("CatalogContents not found")
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)

        return {'catalog_contents': catalog_contents}

    def show(self, req, catalog_id, seq_no):
        """Return Catalog Contents
        :param req: The Request object coming from the wsgi layer
        :param catalog_id: The Catalog id.
        :param seq_no: The Catalog seq_no.
        :retval The response body is a mapping of the following form::
            {'catalog_contents':
                {'catalog_id': <catalog_id>,
                 'seq_no': <seq_no>,
                 'goods_id': <goods_id>,
                 ...}
            }
        """
        self._enforce(req, 'catalog_contents_show')

        self._check_catalog_id(catalog_id)
        self._check_seq_no(seq_no)

        try:
            rtn = self.manager.catalog_contents_show(req.context,
                                                     catalog_id,
                                                     seq_no)

        except exception.NotFound:
            msg = _("Catalog contents not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)

        return dict(catalog_contents=rtn)

    def update(self, req, body, catalog_id, seq_no):
        """Update one of catalog contents
        :param req: The Request object coming from the wsgi layer
        :param body: The request body is a mapping of the following form::
            {'catalog_contents': {
                'goods_id': <goods_id>,
                'goods_num': <goods_num>,
                'expansions': {...},
                ...}
            }
        :param catalog_id: The Catalog id.
        :param seq_no: The Catalog seq_no.
        :retval The response body is a mapping of the following form::
            {'catalog_contents': {
                'catalog_id': <catalog_id>,
                'seq_no': <seq_no>,
                'goods_id': <goods_id>,
                 ...}
            }
        """
        self._enforce(req, 'catalog_contents_update')

        self._check_catalog_id(catalog_id)
        self._check_seq_no(seq_no)

        values = from_dict(copy.deepcopy(body['catalog_contents']))
        self._param_check(values)

        try:
            contents = self.manager.catalog_contents_update(req.context,
                                                            catalog_id,
                                                            seq_no,
                                                            **values)

        except exception.NotFound:
            msg = _("Catalog contents not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)

        return {'catalog_contents': contents}

    def delete(self, req, catalog_id, seq_no):
        """Delete one of catalog contents.
            :param req: Http request.
            :param catalog_id: Catalog id.
            :param seq_no: Seq no.
        """
        self._enforce(req, 'catalog_contents_delete')

        try:
            self.manager.catalog_contents_delete(req.context,
                                                 catalog_id,
                                                 seq_no)
        except exception.NotFound:
            msg = _("Catalog contents not found")
            LOG.error(msg)
            raise webob.exc.HTTPNotFound(msg)


def create_resource():
    """Aflo resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
