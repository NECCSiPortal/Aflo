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

from datetime import datetime
from oslo_config import cfg
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
import aflo.context
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

CATALOG_ID = 'catalog0-1111-2222-3333-000000000001'
SEQ_NO_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
SEQ_NO_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'


def get_datetime(str_date):
    """Get datetime.
        :param str_date: String of date.
    """
    return datetime.strptime(str_date + 'T00:00:00.000000',
                             '%Y-%m-%dT%H:%M:%S.%f')


class TestCatalogContentsDeleteAPI(base.IsolatedUnitTest):
    """Do a test of 'Delete catalog contents'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestCatalogContentsDeleteAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestCatalogContentsDeleteAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        catalog_contents = db_models.CatalogContents
        catalog_contents(catalog_id=CATALOG_ID,
                         seq_no=SEQ_NO_101,
                         goods_id='goods000-1111-2222-3333-000000000001',
                         goods_num=101,
                         deleted=False).save(db_api.get_session())

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_delete(self):
        """Delete a catalog contents"""
        path = '/catalog/%s/contents/%s' % (CATALOG_ID, SEQ_NO_101)
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 200)

        se = db_api.get_session()
        catalog_contents = se.query(db_models.CatalogContents)\
            .filter_by(catalog_id=CATALOG_ID, seq_no=SEQ_NO_101).first()
        self.assertIsNone(catalog_contents)

    def test_delete_api_no_authority(self):
        """Delete a catalog contents with no authority"""
        path = '/catalog/%s/contents/%s' % (CATALOG_ID, SEQ_NO_102)
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 403)

    def test_delete_api_no_exist_irregular(self):
        """Delete a catalog contents which is not exist."""
        path = '/catalog/%s/contents/%s' % (CATALOG_ID, SEQ_NO_102)
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)

    def test_delete_api_error_uri(self):
        """Delete a catalog contents which error uri."""
        path = '/catalog/%s/contents/%s' % (CATALOG_ID, '')
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)
