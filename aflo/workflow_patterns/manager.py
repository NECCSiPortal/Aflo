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

from aflo.db.sqlalchemy import api as db_api


class WorkflowPatternsManager(object):

    def workflow_patterns_get(self, ctxt,
                              workflow_pattern_id,
                              workflow_pattern_code):
        return db_api.workflow_patterns_get(ctxt,
                                            workflow_pattern_id,
                                            workflow_pattern_code)

    def workflow_patterns_create(self, ctxt, **values):
        return db_api.workflow_patterns_create(ctxt, **values)

    def workflow_patterns_delete(self, ctxt,
                                 workflowpattern_id):
        return db_api.workflow_patterns_delete(ctxt, workflowpattern_id)
