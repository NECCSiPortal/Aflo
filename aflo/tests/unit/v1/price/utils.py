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


def create_testdata(db_models, catalog_id, scope, seq_no,
                    price, lifetime_start, lifetime_end,
                    date, seq, deleted=False):

    db_models.Price(catalog_id=catalog_id, scope=scope,
                    seq_no=seq_no, price=price,
                    lifetime_start=lifetime_start,
                    lifetime_end=lifetime_end,
                    expansion_key1=seq, expansion_key2=seq,
                    expansion_key3=seq, expansion_key4=seq,
                    expansion_key5=seq, expansion_text=seq,
                    created_at=date, updated_at=date,
                    deleted=deleted).save()
