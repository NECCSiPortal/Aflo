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
#
#

from oslo_config import cfg

from aflo.common.tickettemplate_expansion_filter_base\
    import TicketTemplateExpansionFilterBase
from aflo.db.sqlalchemy import api as db_api

CONF = cfg.CONF


class ValidRoleExpansionFilter(TicketTemplateExpansionFilterBase):
    """Valid Role Expansion Filter."""

    def do_exec(self, req, ticket_templates):
        """Filtering ticket template.
        Remove the ticket template which does not have a valid role.
        :param req: HTTP request.
        :param ticket_templates: ticket template data.
        """
        if not ticket_templates:
            return ticket_templates

        user_roles = req.context.roles
        # Get all worflow pattern list
        workflow_list = db_api.workflow_patterns_list(req.context)

        for template in ticket_templates[:]:
            workflow = self._get_workflow(workflow_list,
                                          template.workflow_pattern_id)

            has_role = False
            grant_role = self._get_grant_role(workflow)

            for role in grant_role:
                if role in user_roles:
                    has_role = True
                    break
            if not has_role:
                ticket_templates.remove(template)

    def _get_workflow(self, workflow_list, workflow_id):
        for workflow in workflow_list:
            if workflow.id == workflow_id:
                return workflow

    def _get_grant_role(self, workflow):
        all_status_list = workflow.wf_pattern_contents['status_list']
        current_status = filter(
            lambda status:
            status['status_code'] == 'none',
            all_status_list)[0]
        next_status = current_status.get('next_status')
        all_role = []

        for status in next_status:
            grant_role = status.get('grant_role', [])
            if not isinstance(grant_role, list):
                grant_role = [grant_role]

            all_role.extend(grant_role)

        return all_role
