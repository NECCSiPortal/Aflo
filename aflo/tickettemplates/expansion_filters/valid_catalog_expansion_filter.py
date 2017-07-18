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

import datetime

from aflo.common.tickettemplate_expansion_filter_base\
    import TicketTemplateExpansionFilterBase
from aflo.db.sqlalchemy import api as db_api
from oslo_config import cfg

CONF = cfg.CONF


class ValidCatalogExpansionFilter(TicketTemplateExpansionFilterBase):
    """Valid Catalog Expansion Filter."""

    def do_exec(self, req, ticket_templates):
        """Filtering ticket template.
        Remove the ticket template which does not have a valid catalog.
        :param req: HTTP request.
        :param ticket_templates: ticket template data.
        """
        if not ticket_templates:
            return ticket_templates

        tenant_id = req.context.tenant
        utcnow = self._get_datetime_utcnow()

        filters = {'scope': tenant_id,
                   'lifetime': utcnow}

        # get valid catalog list
        valid_catalog = db_api.valid_catalog_list(req.context,
                                                  limit=CONF.api_limit_max,
                                                  refine_flg=False,
                                                  filters=filters)

        for template in ticket_templates[:]:
            if template.ticket_type != CONF.target_ticket_type:
                continue

            if not valid_catalog:
                ticket_templates.remove(template)
                continue

            target_ids = template.template_contents.get('target_id')
            if not target_ids:
                ticket_templates.remove(template)
                continue

            for target_id in target_ids:
                if len(filter(lambda row:
                              row["catalog_id"] == target_id,
                              valid_catalog)) < 1:
                    ticket_templates.remove(template)
                    break

    def _get_datetime_utcnow(self):
        utcnow = datetime.datetime.utcnow()
        return utcnow.strftime('%Y-%m-%dT%H:%M:%S.%f')
