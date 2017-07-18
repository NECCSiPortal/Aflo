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

from aflo.db.sqlalchemy import api as db_api


class CatalogScopeManager(object):

    def catalog_scope_create(self, ctxt, **values):
        return db_api.catalog_scope_create(ctxt, **values)

    def catalog_scope_list(self, ctxt, marker=None, limit=None,
                           sort_key=None, sort_dir=None,
                           force_show_deleted=None, filters=None):
        return db_api.catalog_scope_list(ctxt, marker, limit,
                                         sort_key, sort_dir,
                                         force_show_deleted, filters)

    def catalog_scope_show(self, ctxt, catalog_scope_id):
        return db_api.catalog_scope_get(ctxt, catalog_scope_id)

    def catalog_scope_update(self, ctxt, catalog_scope_id, **values):
        return db_api.catalog_scope_update(ctxt, catalog_scope_id, **values)

    def catalog_scope_delete(self, ctxt, catalog_scope_id):
        return db_api.catalog_scope_delete(ctxt, catalog_scope_id)
