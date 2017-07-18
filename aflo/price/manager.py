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


class PriceManager(object):

    def price_create(self, ctxt, **values):
        return db_api.price_create(ctxt, **values)

    def price_list(self, ctxt, catalog_id,
                   marker=None, limit=None,
                   sort_key=None, sort_dir=None,
                   force_show_deleted=False, filters=None):
        return db_api.price_list(ctxt, catalog_id,
                                 marker, limit,
                                 sort_key, sort_dir,
                                 force_show_deleted,
                                 filters)

    def price_get(self, ctxt, catalog_id, scope, seq_no):
        return db_api.price_get(ctxt, catalog_id, scope, seq_no)

    def price_update(self, ctxt, catalog_id, scope, seq_no, **values):
        return db_api.price_update(ctxt, catalog_id, scope, seq_no, **values)

    def price_delete(self, ctxt, catalog_id, scope, seq_no):
        """Delete price.
            :param ctxt: Http context.
            :param catalog_id: Catalog id.
            :parma scope: Scope.
            :param seq_no: Seq no.
        """
        db_api.price_delete(ctxt, catalog_id, scope, seq_no)
