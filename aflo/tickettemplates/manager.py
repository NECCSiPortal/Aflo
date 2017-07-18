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


class TicketTemplatesManager(object):

    def ticket_templates_create(self, ctxt, **values):

        return db_api.ticket_templates_create(ctxt, **values)

    def ticket_templates_list(self, ctxt,
                              marker=None, limit=None,
                              sort_key=None, sort_dir=None,
                              force_show_deleted=False,
                              ticket_type=None,
                              filters=None):
        return db_api.ticket_templates_list(ctxt, marker, limit,
                                            sort_key, sort_dir,
                                            force_show_deleted,
                                            ticket_type,
                                            filters)

    def ticket_templates_get(self, ctxt,
                             tickettemplate_id):
        return db_api.ticket_templates_get(ctxt, tickettemplate_id)

    def ticket_templates_delete(self, ctxt,
                                tickettemplate_id):
        return db_api.ticket_templates_delete(ctxt, tickettemplate_id)
