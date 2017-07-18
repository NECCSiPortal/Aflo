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

import uuid

from aflo.db.sqlalchemy import models as db_models


# make catalog.
def make_catalog(catalog_name, seq_no, goods_num, nova_key, unit,
                 lifetime_start, lifetime_end):
    role = 'admin'
    catalog_id = str(uuid.uuid4())
    catalog = db_models.Catalog(catalog_id=catalog_id)
    catalog.catalog_name = catalog_name
    catalog.lifetime_start = lifetime_start
    catalog.lifetime_end = lifetime_end
    catalog.save()
    catalog_content = db_models.CatalogContents(catalog_id=catalog_id)
    catalog_content.seq_no = seq_no
    catalog_content.goods_num = goods_num
    catalog_content.expansion_key2 = nova_key
    catalog_content.expansion_key3 = unit
    catalog_content.save()
    catalog_scope = db_models.CatalogScope(catalog_id=catalog_id)
    catalog_scope.id = str(uuid.uuid4())
    catalog_scope.scope = role
    catalog_scope.lifetime_start = lifetime_start
    catalog_scope.lifetime_end = lifetime_end
    catalog_scope.save()
    price = db_models.Price(catalog_id=catalog_id)
    price.seq_no = seq_no
    price.price = '100'
    price.scope = role
    price.lifetime_start = lifetime_start
    price.lifetime_end = lifetime_end
    price.save()

    return catalog_id


# make catalog
def make_catalog_only(catalog_name, seq_no, goods_num, nova_key, unit):
    catalog_id = str(uuid.uuid4())
    catalog = db_models.Catalog(catalog_id=catalog_id)
    catalog.catalog_name = catalog_name
    catalog.save()
    catalog_content = db_models.CatalogContents(catalog_id=catalog_id)
    catalog_content.seq_no = seq_no
    catalog_content.goods_num = goods_num
    catalog_content.expansion_key2 = nova_key
    catalog_content.expansion_key3 = unit
    catalog_content.save()

    return catalog_id
