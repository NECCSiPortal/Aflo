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

import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests.unit.v1.tickets import utils as tickets_utils

CONF = cfg.CONF

LOGIN_USER_TENANT_ID = str(uuid.uuid4())
OTHER_TENANT_ID = str(uuid.uuid4())


class TestTenantFilterAPI(base.WorkflowUnitTest):
    """Users other than the administrator make sure
     that does not have access to the data of other tenants.
    """

    def create_fixtures(self):
        super(TestTenantFilterAPI, self).create_fixtures()

        self.login_user_tenant_data = []
        self.other_tenant_data = []

        # Create login user belongs tenant data
        tickets0, t0_workflows = \
            tickets_utils.create_ticket_for_update(db_models,
                                                   LOGIN_USER_TENANT_ID, 0)
        self.login_user_tenant_data.append({'ticket': tickets0,
                                            'workflows': t0_workflows})
        tickets1, t1_workflows = \
            tickets_utils.create_ticket_for_update(db_models,
                                                   LOGIN_USER_TENANT_ID, 1)
        self.login_user_tenant_data.append({'ticket': tickets1,
                                            'workflows': t1_workflows})

        # Create tenant login user does not belong
        tickets2, t2_workflows = \
            tickets_utils.create_ticket_for_update(db_models,
                                                   OTHER_TENANT_ID, 2)
        self.other_tenant_data.append({'ticket': tickets2,
                                       'workflows': t2_workflows})
        tickets3, t3_workflows = \
            tickets_utils.create_ticket_for_update(db_models,
                                                   OTHER_TENANT_ID, 3)
        self.other_tenant_data.append({'ticket': tickets3,
                                       'workflows': t3_workflows})

    def test_index_api_can_not_show_other_tenant(self):
        """Do a test of 'List Search of tickets'
        That other tenant data is not acquired.
        """

        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:developer' % LOGIN_USER_TENANT_ID}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'],
                         self.login_user_tenant_data[1]['ticket'].id)
        self.assertEqual(res_objs[1]['id'],
                         self.login_user_tenant_data[0]['ticket'].id)

    def test_index_api_admin_can_show_all_tenant(self):
        """Do a test of 'List Search of tickets'
        Admin can see all of tenant data.
        """

        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:admin' % LOGIN_USER_TENANT_ID}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['id'],
                         self.other_tenant_data[1]['ticket'].id)
        self.assertEqual(res_objs[1]['id'],
                         self.other_tenant_data[0]['ticket'].id)
        self.assertEqual(res_objs[2]['id'],
                         self.login_user_tenant_data[1]['ticket'].id)
        self.assertEqual(res_objs[3]['id'],
                         self.login_user_tenant_data[0]['ticket'].id)

    def test_index_api_admin_can_use_tenant_filter(self):
        """Do a test of 'List Search of tickets'
        Admin can use the tenant_filter.
        """

        # Create a request data
        path = '/tickets?tenant_id=%s' % OTHER_TENANT_ID
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:admin' % LOGIN_USER_TENANT_ID}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'],
                         self.other_tenant_data[1]['ticket'].id)
        self.assertEqual(res_objs[1]['id'],
                         self.other_tenant_data[0]['ticket'].id)

    def test_show_api_can_not_show_other_tenant(self):
        """Do a test of 'Get the details of the tickets'
        That other tenant data is not acquired.
        """

        # Create a request data
        path = '/tickets/%s' % self.other_tenant_data[0]['ticket'].id
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:developer' % LOGIN_USER_TENANT_ID}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_api_can_show_self_tenant(self):
        """Do a test of 'Get the details of the tickets'
        Data belongs to tenants I can browse.
        """

        # Create a request data
        path = '/tickets/%s' % self.login_user_tenant_data[0]['ticket'].id
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:developer' % LOGIN_USER_TENANT_ID}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['ticket']
        self.assertEqual(res_objs['id'],
                         self.login_user_tenant_data[0]['ticket'].id)

    def test_show_api_admin_can_show_all_tenant(self):
        """Do a test of 'Get the details of the tickets'
        Admin can see all of tenant data.
        """

        # Create a request data
        path = '/tickets/%s' % self.other_tenant_data[0]['ticket'].id
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:admin' % LOGIN_USER_TENANT_ID}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['ticket']
        self.assertEqual(res_objs['id'],
                         self.other_tenant_data[0]['ticket'].id)
