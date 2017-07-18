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

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.v1.tickets import utils as tickets_utils

CONF = cfg.CONF

WFP_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'

TT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'

WF_UUID1_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02011'
WF_UUID1_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02012'
WF_UUID1_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02013'
WF_UUID2_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02021'
WF_UUID2_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02022'
WF_UUID2_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02023'
WF_UUID3_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02031'
WF_UUID3_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02032'
WF_UUID3_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02033'
WF_UUID4_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02041'
WF_UUID4_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02042'
WF_UUID4_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02043'
WF_UUID5_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02051'
WF_UUID5_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02052'
WF_UUID5_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02053'

T_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef03001'
T_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef03002'

TAR_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef04001'

TEN_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef05001'
TEN_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef05002'

OWN_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef06001'
OWN_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef06002'
OWN_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef06003'


class TestTicketsShowAPI(base.WorkflowUnitTest):
    """Do a test of 'Get the details of the tickets'"""

    def create_fixtures(self):
        super(TestTicketsShowAPI, self).create_fixtures()

        tickets_utils.create_workflow_pattern(db_models, WFP_UUID1, 1)

        tickets_utils.create_ticket_template(db_models, TT_UUID1, WFP_UUID1, 1)

        tickets_utils.create_ticket(db_models, T_UUID1, TT_UUID1,
                                    TAR_UUID1, TEN_UUID1, OWN_UUID1, 1)
        tickets_utils.create_ticket(db_models, T_UUID2, TT_UUID1,
                                    TAR_UUID1, TEN_UUID2, OWN_UUID3, 2)

        tickets_utils.create_workflow(db_models, WF_UUID1_1, T_UUID1, 2,
                                      'applied', '__member__',
                                      'confirmer01',
                                      datetime.date(2015, 1, 10), 1)
        tickets_utils.create_workflow(db_models, WF_UUID1_2, T_UUID1, 1,
                                      'applied_1st', 'director', None,
                                      None, 2)
        tickets_utils.create_workflow(db_models, WF_UUID1_3, T_UUID1, 0,
                                      'applied_2nd', 'tenant_admin', None,
                                      None, 3)

        tickets_utils.create_workflow(db_models, WF_UUID2_1, T_UUID2, 2,
                                      'applied', '__member__',
                                      'confirmer02',
                                      datetime.date(2015, 1, 10), 1)
        tickets_utils.create_workflow(db_models, WF_UUID2_2, T_UUID2, 2,
                                      'applied_1st', 'director',
                                      'confirmer03',
                                      datetime.date(2015, 1, 13), 2)
        tickets_utils.create_workflow(db_models, WF_UUID2_3, T_UUID2, 1,
                                      'applied_2nd', 'tenant_admin', None,
                                      None, 3)

    def test_show(self):
        """Do a test of 'Get the details of the tickets'
        Test of the normal system.
        """
        path = '/tickets/%s' % T_UUID1

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['ticket']
        self.assertEqual(res_objs['id'], T_UUID1)

    def test_show_response_empty_irregular(self):
        """Do a test of 'Get the details of the tickets'
        DB don't have an applicable data.
        """

        path = '/tickets/aaa'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_api_no_authority(self):
        """Test show api.
        User don't have admin authority.
        """
        path = '/tickets/%s' % T_UUID1

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_show_roles_return(self):
        """Do a test of 'Get the details of the tickets'
        Or test "roles" is to return value has been added.
        """
        path = '/tickets/%s' % T_UUID1

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin,developer,__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['ticket']
        self.assertEqual(res_objs['roles'][0], 'admin')
        self.assertEqual(res_objs['roles'][1], 'developer')
        self.assertEqual(res_objs['roles'][2], '__member__')
