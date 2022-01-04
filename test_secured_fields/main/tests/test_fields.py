from unittest.case import skip
from django import test
from django.db import connection
from django.db.models import Model

from main import models
from secured_fields.fernet import get_fernet


class BaseTestCases:

    class BaseFieldTestCase(test.TestCase):
        model_class: Model

        def get_raw_field(self):
            with connection.cursor() as cursor:
                # pylint: disable=protected-access
                cursor.execute(f'SELECT field FROM {self.model_class._meta.db_table} LIMIT 1')
                return cursor.fetchone()[0]

        def assertIsEncryptedNone(self):
            self.assertIsNone(self.get_raw_field())

        def assertEncryptedField(self, expected_bytes: bytes):
            field_value = self.get_raw_field()
            decrypted_value = get_fernet().decrypt(field_value)

            self.assertEqual(decrypted_value, expected_bytes)

        def test_null(self):
            model = self.model_class.objects.create(field=None)

            self.assertIsNone(model.field)
            self.assertIsEncryptedNone()


class BooleanFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.BooleanFieldModel

    def test_simple(self):
        model = self.model_class.objects.create(field=True)

        self.assertEqual(model.field, True)
        self.assertEncryptedField(b'True')


class CharFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.CharFieldModel

    def test_simple(self):
        model = self.model_class.objects.create(field='test')

        self.assertEqual(model.field, 'test')
        self.assertEncryptedField(b'test')


class IntegerFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.IntegerFieldModel

    def test_simple(self):
        model = self.model_class.objects.create(field=100)

        self.assertEqual(model.field, 100)
        self.assertEncryptedField(b'100')


class TextFieldTestCase(BaseTestCases.BaseFieldTestCase):
    model_class = models.TextFieldModel

    def test_simple(self):
        model = self.model_class.objects.create(field='test')

        self.assertEqual(model.field, 'test')
        self.assertEncryptedField(b'test')
