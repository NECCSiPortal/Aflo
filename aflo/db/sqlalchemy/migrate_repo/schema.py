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
Various conveniences used for migration scripts
"""

from oslo_log import log as logging
import sqlalchemy.types

from aflo import i18n


LOG = logging.getLogger(__name__)
_LI = i18n._LI


String = lambda length: sqlalchemy.types.String(
    length=length, convert_unicode=False,
    unicode_error=None, _warn_on_bytestring=False)


Text = lambda length: sqlalchemy.types.Text(
    length=length, convert_unicode=False,
    unicode_error=None, _warn_on_bytestring=False)


Boolean = lambda: sqlalchemy.types.Boolean(create_constraint=True, name=None)


DateTime = lambda: sqlalchemy.types.DateTime(timezone=False)


Integer = lambda: sqlalchemy.types.Integer()


BigInteger = lambda: sqlalchemy.types.BigInteger()


PickleType = lambda: sqlalchemy.types.PickleType()


Numeric = lambda precision, scale: sqlalchemy.types.Numeric(
    precision=precision, scale=scale, asdecimal=True)


TextContract = lambda: sqlalchemy.types.Text(
    convert_unicode=False,
    unicode_error=None, _warn_on_bytestring=False)


def from_migration_import(module_name, fromlist):
    """
    Import a migration file and return the module

    :param module_name: name of migration module to import from
        (ex: 001_add_afloobjs_table)
    :param fromlist: list of items to import (ex: define_afloobjs_table)
    :retval: module object

    This bit of ugliness warrants an explanation:

        As you're writing migrations, you'll frequently want to refer to
        tables defined in previous migrations.

        In the interest of not repeating yourself, you need a way of importing
        that table into a 'future' migration.

        However, tables are bound to metadata, so what you need to import is
        really a table factory, which you can late-bind to your current
        metadata object.

        Moreover, migrations begin with a number (001...), which means they
        aren't valid Python identifiers. This means we can't perform a
        'normal' import on them (the Python lexer will 'splode). Instead, we
        need to use __import__ magic to bring the table-factory into our
        namespace.

    Example Usage:

        (define_afloobjs_table,) = from_migration_import(
            '001_add_afloobjs_table', ['define_afloobjs_table'])

        afloobjs = define_afloobjs_table(meta)

        # Refer to afloobjs table
    """
    module_path = 'aflo.db.sqlalchemy.migrate_repo.versions.%s' % module_name
    module = __import__(module_path, globals(), locals(), fromlist, -1)
    return [getattr(module, item) for item in fromlist]


def create_tables(tables):
    for table in tables:
        LOG.info(_LI("creating table %(table)s") % {'table': table})
        table.create()


def drop_tables(tables):
    for table in tables:
        LOG.info(_LI("dropping table %(table)s") % {'table': table})
        table.drop()
