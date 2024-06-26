import json

from django.db.models import lookups

from . import mixins, utils


class EncryptedExact(lookups.EndsWith):

    def as_sql(self, compiler, connection):
        sql, params = super().as_sql(compiler, connection)

        # search using hash
        hashed = utils.hash_with_salt(params[0][1:])
        params[0] = '%' + mixins.EncryptedMixin.separator + hashed

        return sql, params


class EncryptedJSONExact(EncryptedExact):

    def get_db_prep_lookup(self, value, connection):
        value = json.dumps(value)

        return super().get_db_prep_lookup(value, connection)


class EncryptedIn(lookups.In):

    def get_rhs_op(self, connection, rhs):  # pylint: disable=unused-argument
        return lookups.EndsWith(self.lhs, '%s').get_rhs_op(connection, '%s')

    def as_sql(self, compiler, connection):
        sql, params = super().as_sql(compiler, connection)

        # reformat to multiple OR condition instead
        sql += (' OR ' + sql) * (len(params) - 1)
        sql = f'({sql})'

        # search using hash for each item
        params = [
            '%' + mixins.EncryptedMixin.separator + utils.hash_with_salt(str(param))
            for param in params
        ]

        return sql, params
