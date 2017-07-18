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
import aflo.context
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy.models import CatalogContents
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

CT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
CT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'
CT_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef00003'
CT_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef00004'

body01 = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 3,
        "deleted": True,
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body02 = {
    "catalog_contents": {
        "goods_id": 'goods001',
    }
}
body03 = {
    "catalog_contents": {}
}
body04 = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": None,
        "expansions": {
            "expansion_key1": None,
            "expansion_key2": None,
            "expansion_key3": None,
            "expansion_key4": None,
            "expansion_key5": None
        },
        "expansions_text": {
            "expansion_text": None
        }
    }
}
body_goods_id_error = {
    "catalog_contents": {
        "goods_id": 'a' * 65,
        "goods_num": 3,
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_goods_num_error_not_int = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 'a',
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_goods_num_error = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 10000,
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key1_error = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 3,
        "expansions": {
            "expansion_key1": 'a' * 256,
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key2_error = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 3,
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": 'a' * 256,
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key3_error = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 3,
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": 'a' * 256,
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key4_error = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 3,
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": 'a' * 256,
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key5_error = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 3,
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": 'a' * 256
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_text_error = {
    "catalog_contents": {
        "goods_id": 'goods001',
        "goods_num": 3,
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": 'a' * 4001
        }
    }
}


class TestCatalogContentsShowAPI(base.WorkflowUnitTest):
    """Test 'Update the details of the CatalogContents'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestCatalogContentsShowAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestCatalogContentsShowAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        CatalogContents(catalog_id=CT_UUID1,
                        seq_no='1',
                        goods_id='1',
                        goods_num=1,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())
        CatalogContents(catalog_id=CT_UUID1,
                        seq_no='2',
                        goods_id='1',
                        goods_num=1,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())
        CatalogContents(catalog_id=CT_UUID2,
                        seq_no='1',
                        goods_id='1',
                        goods_num=1,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())
        CatalogContents(catalog_id=CT_UUID2,
                        seq_no='2',
                        goods_id='1',
                        goods_num=1,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=True,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

    def test_catalog_contents_update_api(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        contents = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(contents['catalog_id'], CT_UUID1)
        self.assertEqual(contents['seq_no'], '1')
        self.assertEqual(contents['goods_id'], 'goods001')
        self.assertEqual(contents['goods_num'], 3)
        self.assertEqual(contents['expansions']['expansion_key1'], '1')
        self.assertEqual(contents['expansions']['expansion_key2'], '2')
        self.assertEqual(contents['expansions']['expansion_key3'], '3')
        self.assertEqual(contents['expansions']['expansion_key4'], '4')
        self.assertEqual(contents['expansions']['expansion_key5'], '5')
        self.assertEqual(contents['expansions_text']['expansion_text'], '0')
        self.assertIsNotNone(contents['created_at'])
        self.assertIsNotNone(contents['updated_at'])
        self.assertIsNone(contents['deleted_at'])
        self.assertEqual(contents['deleted'], False)

    def test_catalog_contents_update_no_auth_irregular(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body02)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_catalog_contents_update_no_keyword(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body03)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        contents = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(contents['catalog_id'], CT_UUID1)
        self.assertEqual(contents['seq_no'], '1')
        self.assertEqual(contents['goods_id'], '1')
        self.assertEqual(contents['goods_num'], 1)
        self.assertEqual(contents['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(contents['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(contents['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(contents['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(contents['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(contents['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(contents['created_at'])
        self.assertIsNotNone(contents['updated_at'])
        self.assertIsNone(contents['deleted_at'])
        self.assertEqual(contents['deleted'], False)

    def test_catalog_contents_update_none_value(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body04)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        contents = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(contents['catalog_id'], CT_UUID1)
        self.assertEqual(contents['seq_no'], '1')
        self.assertIsNone(contents['goods_id'])
        self.assertIsNone(contents['goods_num'])
        self.assertIsNone(contents['expansions']['expansion_key1'])
        self.assertIsNone(contents['expansions']['expansion_key2'])
        self.assertIsNone(contents['expansions']['expansion_key3'])
        self.assertIsNone(contents['expansions']['expansion_key4'])
        self.assertIsNone(contents['expansions']['expansion_key5'])
        self.assertIsNone(contents['expansions_text']['expansion_text'])
        self.assertIsNotNone(contents['created_at'])
        self.assertIsNotNone(contents['updated_at'])
        self.assertIsNone(contents['deleted_at'])
        self.assertEqual(contents['deleted'], False)

    def test_catalog_contents_update_catalog_id_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % ('a' * 65, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_seq_no_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, 'a' * 65)
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_goods_id_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_goods_id_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_goods_num_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_goods_num_error_not_int)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_goods_num_error_int(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_goods_num_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_expansion_key1_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_expansion_key2_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_expansion_key3_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_expansion_key4_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_expansion_key5_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_expansion_text_error(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_catalog_contents_update_nodata_irregular(self):
        # Create a request data
        path = '/catalog/%s/contents/%s' \
               % (CT_UUID3, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)
