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

import os

from oslo_concurrency import lockutils
from oslo_config import cfg
from oslo_db import options
from oslo_serialization import jsonutils
import routes

import aflo.api
from aflo.api.v1 import router
import aflo.common.config
from aflo.common import wsgi
import aflo.context
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.tests import utils as test_utils

CONF = cfg.CONF


class IsolatedUnitTest(test_utils.BaseTestCase):

    """
    Unit test case that establishes a mock environment within
    a testing directory (in isolation)
    """

    def setUp(self):
        super(IsolatedUnitTest, self).setUp()
        options.set_defaults(CONF, connection='sqlite://',
                             sqlite_db='aflo.sqlite')
        lockutils.set_defaults(os.path.join(self.test_dir))

        self.config(debug=False)

    def set_policy_rules(self, rules):
        fap = open(CONF.oslo_policy.policy_file, 'w')
        fap.write(jsonutils.dumps(rules))
        fap.close()


class WorkflowUnitTest(IsolatedUnitTest):
    """Base class to implement the unit test of 'workflow engine'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(WorkflowUnitTest, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.serializer = wsgi.JSONResponseSerializer()
        self.destroy_fixtures()
        self.create_fixtures()

    def tearDown(self):
        """Clear the test environment"""
        super(WorkflowUnitTest, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        pass

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())
