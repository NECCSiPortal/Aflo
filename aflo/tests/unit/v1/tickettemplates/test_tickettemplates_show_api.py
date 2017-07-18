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

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests.unit.v1.tickettemplates\
    import utils as t_templates_utils

CONF = cfg.CONF

WF_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
WF_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'
WF_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef00003'
WF_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef00004'
WF_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef00005'

TT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
TT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'
TT_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef01003'
TT_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef01004'
TT_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef01005'
TT_UUID6 = 'ea0a4146-fd07-414b-aa5e-dedbeef010XX'


class TestTicketTemplatesShowAPI(base.WorkflowUnitTest):
    """Do a test of 'Get the details of the tickettemplates'"""

    def create_fixtures(self):
        super(TestTicketTemplatesShowAPI, self).create_fixtures()

        t_templates_utils.create_testdata(db_models, TT_UUID1, WF_UUID1, 1)
        t_templates_utils.create_testdata(db_models, TT_UUID2, WF_UUID2, 2)
        t_templates_utils.create_testdata(db_models, TT_UUID3, WF_UUID3, 3)
        t_templates_utils.create_testdata(db_models, TT_UUID4, WF_UUID4, 4,
                                          ticket_template_delete=True)
        t_templates_utils.create_ticket_template(db_models, TT_UUID5,
                                                 WF_UUID1, 5)

    def test_show(self):
        """Do a test of 'Get the details of the tickettemplates'
        Test of the normal system.
        """

        path = '/tickettemplates/%s' % TT_UUID1

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplate']
        self.assertEqual(res_objs['id'], TT_UUID1)

        # To make sure that was get "workflow_pattern"
        self.assertEqual(res_objs['workflow_pattern']['id'], WF_UUID1)

    def test_show_response_empty_irregular(self):
        """Do a test of 'Get the details of the tickettemplates'
        DB don't have an applicable data.
        """

        path = '/tickettemplates/aaa'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
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
        path = '/tickettemplates/%s' % TT_UUID1

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_show_api_no_tickettemplate(self):
        """Test show api.
        Get not exists ticket template.
        """
        path = '/tickettemplates/%s' % TT_UUID6

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)
