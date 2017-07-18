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

GOODS_DATA_LIST = [
    {
        "goods_name": "VCPU"
    },
    {
        "goods_name": "RAM"
    },
    {
        "goods_name": "Volume Storage"
    }
]

CATALOG_DATA_LIST = [
    {
        "catalog_name": "VCPU x 10 CORE(S)",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
    {
        "catalog_name": "RAM 20 GB",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
    {
        "catalog_name": "Volume Storage 50 GB",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    }
]

INVALID_CATALOG_DATA_LIST = [
    {
        "catalog_name": "VCPU x 10 CORE(S)",
        "lifetime_start": "2000-01-01T00:00:00.000000",
        "lifetime_end": "2000-12-31T00:00:00.000000"
    },
    {
        "catalog_name": "RAM 20 GB",
        "lifetime_start": "2000-01-01T00:00:00.000000",
        "lifetime_end": "2000-12-31T00:00:00.000000"
    },
    {
        "catalog_name": "Volume Storage 50 GB",
        "lifetime_start": "2000-01-01T00:00:00.000000",
        "lifetime_end": "2000-12-31T00:00:00.000000"
    }
]

CATALOG_CONTENTS_DATA_LIST = [
    {
        "goods_num": 10,
        "expansion_key2": "cores",
        "expansion_key3": ""
    },
    {
        "goods_num": 20,
        "expansion_key2": "ram",
        "expansion_key3": "GB"
    },
    {
        "goods_num": 50,
        "expansion_key2": "gigabytes",
        "expansion_key3": "GB"
    }
]

PRICE_DATA_LIST = [
    {
        "scope": "Default",
        "price": 172.41,
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
    {
        "scope": "Default",
        "price": 258.62,
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
    {
        "scope": "Default",
        "price": 64.66,
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
]

INVALID_PRICE_DATA_LIST = [
    {
        "scope": "Default",
        "price": 172.41,
        "lifetime_start": "2000-01-01T00:00:00.000000",
        "lifetime_end": "2000-12-31T00:00:00.000000"
    },
    {
        "scope": "Default",
        "price": 258.62,
        "lifetime_start": "2000-01-01T00:00:00.000000",
        "lifetime_end": "2000-12-31T00:00:00.000000"
    },
    {
        "scope": "Default",
        "price": 64.66,
        "lifetime_start": "2000-01-01T00:00:00.000000",
        "lifetime_end": "2000-12-31T00:00:00.000000"
    },
]

CATALOG_SCOPE_DATA_LIST = [
    {
        "scope": "Default",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
    {
        "scope": "Default",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
    {
        "scope": "Default",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
]

INVALID_CATALOG_SCOPE_DATA_LIST = [
    {
        "scope": "Default",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
    {
        "scope": "Default",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
    {
        "scope": "Default",
        "lifetime_start": "2015-01-01T00:00:00.000000",
        "lifetime_end": "2999-12-31T00:00:00.000000"
    },
]
