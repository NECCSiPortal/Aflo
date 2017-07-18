#!/usr/bin/env python

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

"""
Aflo API Server
"""

import os
import sys

import eventlet

from aflo.common import utils
from aflo.openstack.common import service

# Monkey patch socket, time, select, threads
eventlet.patcher.monkey_patch(all=False, socket=True, time=True,
                              select=True, thread=True, os=True)

# If ../aflo/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(possible_topdir, 'aflo', '__init__.py')):
    sys.path.insert(0, possible_topdir)

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging

from aflo.common import config
from aflo.common import exception
from aflo.common import wsgi
from aflo.tickets import manager


CONF = cfg.CONF
logging.register_options(CONF)

KNOWN_EXCEPTIONS = (RuntimeError,
                    exception.WorkerCreationFailure)


def fail(e):
    global KNOWN_EXCEPTIONS
    return_code = KNOWN_EXCEPTIONS.index(type(e)) + 1
    sys.stderr.write("ERROR: %s\n" % utils.exception_to_str(e))
    sys.exit(return_code)


def main():
    try:
        config.parse_args()
        wsgi.set_eventlet_hub()
        logging.setup(CONF, 'aflo')

        transport = oslo_messaging.get_transport(cfg.CONF)
        target = oslo_messaging.Target(topic='aflo_topic',
                                       server='server1',
                                       version='1.0')
        endpoints = [
            manager.TicketsManager(),
        ]
        rpc_server = oslo_messaging.get_rpc_server(
            transport,
            target,
            endpoints,
            executor='blocking')

        serve(rpc_server, cfg.CONF.rpc_workers)
        wait()

    except KNOWN_EXCEPTIONS as e:
        fail(e)


_launcher = None


def serve(server, workers=None):
    global _launcher
    if _launcher:
        raise RuntimeError('serve() can only be called once')

    _launcher = service.launch(server, workers=workers)


def wait():
    _launcher.wait()


if __name__ == '__main__':
    main()
