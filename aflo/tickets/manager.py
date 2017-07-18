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

import aflo.context
from aflo.db.sqlalchemy import api as db_api


class TicketsManager(object):

    def tickets_list(self, ctxt,
                     marker=None, limit=None,
                     sort_key=None, sort_dir=None,
                     force_show_deleted=False, filters=None):
        return db_api.tickets_list(ctxt, marker, limit,
                                   sort_key, sort_dir,
                                   force_show_deleted, filters)

    def tickets_get(self, ctxt, ticket_id):
        return db_api.tickets_get(ctxt, ticket_id)

    def tickets_create(self, ctxt, **values):
        ctxt = aflo.context.RequestContext.from_dict(ctxt)
        return db_api.tickets_create(ctxt, **values)

    def tickets_update(self, ctxt, ticket_id, **values):
        ctxt = aflo.context.RequestContext.from_dict(ctxt)
        return db_api.tickets_update(ctxt, ticket_id, **values)

    def tickets_delete(self, ctxt, ticket_id):
        ctxt = aflo.context.RequestContext.from_dict(ctxt)
        return db_api.tickets_delete(ctxt, ticket_id)
