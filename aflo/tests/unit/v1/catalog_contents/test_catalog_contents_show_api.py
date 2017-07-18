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
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
from aflo import context
from aflo import db
from aflo.db.sqlalchemy import models as db_models
from aflo.db.sqlalchemy.models import CatalogContents
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

CATALOG_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CATALOG_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'
CATALOG_ID_103 = 'ea0a4146-fd07-414b-aa5e-dedbeef00103'
CATALOG_ID_104 = 'ea0a4146-fd07-414b-aa5e-dedbeef00104'


class TestAPI(base.IsolatedUnitTest):
    def setUp(self):
        """Establish a clean test environment"""
        super(TestAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_101',
                        goods_id='goods_id_101',
                        goods_num=101,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='1',
                        expansion_key2='1',
                        expansion_key3='1',
                        expansion_key4='1',
                        expansion_key5='1',
                        expansion_text='1'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_102',
                        goods_id='goods_id_101',
                        goods_num=102,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='1',
                        expansion_key2='2',
                        expansion_key3='3',
                        expansion_key4='4',
                        expansion_key5='5',
                        expansion_text='0'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_103',
                        goods_id='goods_id_102',
                        goods_num=101,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='1',
                        expansion_key2=None,
                        expansion_key3=None,
                        expansion_key4=None,
                        expansion_key5=None,
                        expansion_text=None
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_104',
                        goods_id='goods_id_102',
                        goods_num=102,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1=None,
                        expansion_key2=None,
                        expansion_key3=None,
                        expansion_key4=None,
                        expansion_key5=None,
                        expansion_text=None
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_102,
                        seq_no='seq_no_101',
                        goods_id='goods_id_103',
                        goods_num=103,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        deleted_at=datetime.utcnow(),
                        deleted=True,
                        expansion_key1='1',
                        expansion_key2='1',
                        expansion_key3='1',
                        expansion_key4='1',
                        expansion_key5='1',
                        expansion_text='1'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_102,
                        seq_no='seq_no_102',
                        goods_id='goods_id_104',
                        goods_num=104,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='1',
                        expansion_key2='1',
                        expansion_key3='1',
                        expansion_key4='1',
                        expansion_key5='1',
                        expansion_text='1'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_104,
                        seq_no='seq_no_101',
                        goods_id='goods_id_107',
                        goods_num=107,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='!"#$%&()=~|`{+*}<>?_',
                        expansion_key2='!"#$%&()=~|`{+*}<>?_',
                        expansion_key3='!"#$%&()=~|`{+*}<>?_',
                        expansion_key4='!"#$%&()=~|`{+*}<>?_',
                        expansion_key5='!"#$%&()=~|`{+*}<>?_',
                        expansion_text=',./\;:]@[\^-'
                        ).save(db_api.get_session())

    def destroy_fixtures(self):
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_show(self):
        # Test 'Get of catalog contents'
        # Test the operation of default.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_101, 'seq_no_101')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(res_objs['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')

    def test_show_response_empty_catalogid_irregular(self):
        # Test 'Get of catalog contents'
        # Test if the retrieved result is of 0.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_103, 'seq_no_101')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_response_empty_seqno_irregular(self):
        # Test 'Get of catalog contents'
        # Test if the retrieved result is of 0.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_102, 'seq_no_103')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_api_no_authority(self):
        # Test 'Get of catalog contents'
        # Test cases run unauthorized.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_101, 'seq_no_101')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_show_api_symbol(self):
        # Test 'Get of catalog contents'
        # Test the operation of symbol.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_104, 'seq_no_101')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(res_objs['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs['expansions']['expansion_key1'],
                         '!"#$%&()=~|`{+*}<>?_')
        self.assertEqual(res_objs['expansions_text']['expansion_text'],
                         ',./\;:]@[\^-')

    def test_show_api_response_all_expansions(self):
        # Test 'Get of catalog contents'
        # Test if the retrieved result is all expansions.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_101, 'seq_no_102')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(res_objs['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')
        self.assertEqual(res_objs['expansions']['expansion_key2'], '2')
        self.assertEqual(res_objs['expansions']['expansion_key3'], '3')
        self.assertEqual(res_objs['expansions']['expansion_key4'], '4')
        self.assertEqual(res_objs['expansions']['expansion_key5'], '5')
        self.assertEqual(res_objs['expansions_text']['expansion_text'], '0')

    def test_show_api_response_one_expansions(self):
        # Test 'Get of catalog contents'
        # Test if the retrieved result is one expansion_key.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_101, 'seq_no_103')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(res_objs['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')
        self.assertIsNone(res_objs['expansions']['expansion_key2'])
        self.assertIsNone(res_objs['expansions']['expansion_key3'])
        self.assertIsNone(res_objs['expansions']['expansion_key4'])
        self.assertIsNone(res_objs['expansions']['expansion_key5'])
        self.assertIsNone(res_objs['expansions_text']['expansion_text'])

    def test_show_api_response_none_expansions(self):
        # Test 'Get of catalog contents'
        # Test if the retrieved result is non expansion_key.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_101, 'seq_no_104')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(res_objs['seq_no'], 'seq_no_104')
        self.assertIsNone(res_objs['expansions']['expansion_key1'])
        self.assertIsNone(res_objs['expansions']['expansion_key2'])
        self.assertIsNone(res_objs['expansions']['expansion_key3'])
        self.assertIsNone(res_objs['expansions']['expansion_key4'])
        self.assertIsNone(res_objs['expansions']['expansion_key5'])
        self.assertIsNone(res_objs['expansions_text']['expansion_text'])

    def test_show_seq_no_error(self):
        # Test 'Get of catalog contents'
        # Test the operation of default.
        path = '/catalog/%s/contents/%s' % (CATALOG_ID_101, 'a' * 65)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_show_goods_id_error(self):
        # Test 'Get of catalog contents'
        # Test the operation of default.
        path = '/catalog/%s/contents/%s' % ('a' * 65, 'seq_no_101')
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
