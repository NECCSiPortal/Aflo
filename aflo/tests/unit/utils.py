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

import urllib

from oslo_config import cfg
from oslo_log import log as logging
import six.moves.urllib.parse as urlparse

from aflo.common import wsgi
import aflo.context


CONF = cfg.CONF
LOG = logging.getLogger(__name__)

UUID1 = 'c80a1a6c-bd1f-41c5-90ee-81afedb1d58d'
UUID2 = '971ec09a-8067-4bc8-a91f-ae3557f1c4c7'

TENANT1 = '6838eb7b-6ded-434a-882c-b344c77fe8df'
TENANT2 = '2c014f32-55eb-467d-8fcb-4bd706012f81'

USER1 = '54492ba0-f4df-4e4e-be62-27f4d76b29cf'
USER2 = '0b3b3006-cb76-4517-ae32-51397e22c754'
USER3 = '2hss8dkl-d8jh-88yd-uhs9-879sdjsd8skd'

BASE_URI = 'http://storeurl.com/container'


def sort_url_by_qs_keys(url):
    # NOTE(kragniz): this only sorts the keys of the query string of a url.
    # For example, an input of '/v2/tasks?sort_key=id&sort_dir=asc&limit=10'
    # returns '/v2/tasks?limit=10&sort_dir=asc&sort_key=id'. This is to prevent
    # non-deterministic ordering of the query string causing problems with unit
    # tests.

    parsed = urlparse.urlparse(url)
    queries = urlparse.parse_qsl(parsed.query, True)
    sorted_query = sorted(queries, key=lambda x: x[0])

    encoded_sorted_query = urllib.urlencode(sorted_query, True)

    url_parts = (parsed.scheme, parsed.netloc, parsed.path,
                 parsed.params, encoded_sorted_query,
                 parsed.fragment)

    return urlparse.urlunparse(url_parts)


def get_fake_request(path='', method='POST', is_admin=False, user=USER1,
                     roles=['member'], tenant=TENANT1):
    req = wsgi.Request.blank(path)
    req.method = method

    kwargs = {
        'user': user,
        'tenant': tenant,
        'roles': roles,
        'is_admin': is_admin,
    }

    req.context = aflo.context.RequestContext(**kwargs)
    return req


def fake_get_size_from_backend(uri, context=None):
    return 1


def create_fake_objects(args):
    """Create FakeObjects
    :param args: list object having a dict object
                 as a each element.
    :return FakeObject list item by args-dict
    """
    return [FakeObject(dic) for dic in args]


class FakeObject(object):
    def __init__(self, attribute=None):
        """FakeObject constractor
        :param attribute: set a dict object.
                          a key is new attribute and set a value.
        """
        if attribute:
            for key, value in attribute.items():
                setattr(self, key, value)

    def setattr(self, key, value):
        setattr(self, key, value)
