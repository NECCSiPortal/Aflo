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


class GoodsManager(object):

    def goods_create(self, ctxt, **values):
        return db_api.goods_create(ctxt, **values)

    def goods_update(self, ctxt, goods_id, **values):
        """Update goods.
            :param ctxt: Http context.
            :param goods_id: Goods_id.
            :param values: Goods values.
        """
        return db_api.goods_update(ctxt, goods_id, **values)

    def goods_list(self, ctxt, **values):
        return db_api.goods_list(ctxt, **values)

    def goods_get(self, ctxt, goods_id):
        return db_api.goods_get(ctxt, goods_id)

    def goods_delete(self, ctxt, goods_id):
        """Delete goods.
            :param ctxt: Http context.
            :param goods_id: Goods id.
        """
        db_api.goods_delete(ctxt, goods_id)
