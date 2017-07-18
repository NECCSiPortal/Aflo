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


class CatalogContentsManager(object):

    def catalog_contents_create(self, ctxt, **values):
        return db_api.catalog_contents_create(ctxt, **values)

    def catalog_contents_list(self, ctxt, catalog_id,
                              limit=None, marker=None,
                              sort_key=None, sort_dir=None,
                              force_show_deleted=False):
        """Get all CatalogContents that match zero or more filters.
        :param catalog_id: catalog_id of CatalogContents.
        :param limit: maximum number of images to return.
        :param marker: id after which to start page.
        :param sort_key: catalog_contents attribute by
                which results should be sorted.
        :param sort_dir: dict in which results should be sorted (asc, desc).
        :param force_show_deleted: view the deleted deterministic.
        """
        return db_api.catalog_contents_list(ctxt, catalog_id,
                                            limit, marker,
                                            sort_key, sort_dir,
                                            force_show_deleted)

    def catalog_contents_show(self, ctxt, catalog_id, seq_no):
        return db_api.catalog_contents_get(ctxt, catalog_id, seq_no)

    def catalog_contents_update(self, ctxt, catalog_id, seq_no, **values):
        return db_api.catalog_contents_update(ctxt,
                                              catalog_id,
                                              seq_no,
                                              **values)

    def catalog_contents_delete(self, ctxt, catalog_id, seq_no):
        """Delete catalog contents.
            :param ctxt: Http context.
            :param catalog_id: Catalog id.
            :param seq_no: Seq no.
        """
        db_api.catalog_contents_delete(ctxt, catalog_id, seq_no)
