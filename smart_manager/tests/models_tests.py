from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase
from django_dynamic_fixture import G, N

from smart_manager import SmartManager
from smart_manager.tests.models import UpsertModel


class ValidationTest(TransactionTestCase):
    """
    Tests that validation works appropriately.
    """
    def test_invalid_load_path(self):
        """
        Tests that a validation error is raised on an invalid class path for the smart manager.
        """
        smart_manager = N(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.InvalidModelTemplate',
            template={},
        )
        with self.assertRaises(ValidationError):
            smart_manager.clean()

    def test_invalid_template(self):
        """
        Tests that a validation error is raised on an invalid template
        """
        smart_manager = N(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertModelListTemplate',
            template={'invalid': 'invalid'},
        )
        with self.assertRaises(ValidationError):
            smart_manager.clean()

    def test_valid_template(self):
        """
        Tests that a validation error is not raised on a valid template
        """
        self.assertFalse(UpsertModel.objects.exists())
        smart_manager = N(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertModelListTemplate',
            template=[{
                'char_field': 'valid',
                'int_field': 1
            }],
        )
        smart_manager.clean()


class SmartManagerTest(TestCase):
    """
    Tests custom functionality in the SmartManager class.
    """
    def test_unicode(self):
        smart_manager = SmartManager(name='hi')
        self.assertEquals(smart_manager.__unicode__(), 'hi')

    def test_template_changes(self):
        """
        Tests chaning the template and resaving.
        """
        smart_manager = G(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertModelListTemplate',
            template=[{
                'char_field': 'hi',
                'int_field': 1,
            }, {
                'char_field': 'hello',
                'int_field': 2,
            }],
        )

        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

        smart_manager.template = [{
            'char_field': 'hi',
            'int_field': 1,
        }]
        smart_manager.save()

        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())

        smart_manager.delete()
        self.assertFalse(UpsertModel.objects.exists())

    def test_template_changes_no_deletions(self):
        """
        Tests chaning the template and resaving when the template model does not manage deletions.
        """
        smart_manager = G(
            SmartManager,
            manages_deletions=False,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertModelListTemplate',
            template=[{
                'char_field': 'hi',
                'int_field': 1,
            }, {
                'char_field': 'hello',
                'int_field': 2,
            }],
        )

        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

        smart_manager.template = [{
            'char_field': 'hi',
            'int_field': 1,
        }]
        smart_manager.save()

        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

        smart_manager.delete()
        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

    def test_build_multiple_distinct_objs_delete(self):
        smart_manager = G(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertModelListTemplate',
            template=[{
                'char_field': 'hi',
                'int_field': 1,
            }, {
                'char_field': 'hello',
                'int_field': 2,
            }],
        )
        # Simulate re-saving
        smart_manager.save()

        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

        smart_manager.delete()
        self.assertFalse(UpsertModel.objects.exists())

    def test_build_multiple_same_objs(self):
        smart_manager = G(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertModelListTemplate',
            template=[{
                'char_field': 'hi',
                'int_field': 1,
            }, {
                'char_field': 'hi',
                'int_field': 1,
            }],
        )
        # Simulate re-saving
        smart_manager.save()

        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())

        smart_manager.delete()
        self.assertFalse(UpsertModel.objects.exists())

    def test_deletion_valid_obj_deletions_set(self):
        """
        Tests deletion of a valid object when deletions are set.
        """
        smart_manager = G(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertSmartManager',
            template={
                'char_field': 'hi',
                'int_field': 1,
            },
        )
        # Simulate re-saving
        smart_manager.save()

        upsert_model = UpsertModel.objects.get()
        self.assertEquals(upsert_model.char_field, 'hi')
        self.assertEquals(upsert_model.int_field, 1)

        # Delete the model template object, resulting in the deleting of the object it manages
        smart_manager.delete()
        self.assertEquals(UpsertModel.objects.count(), 0)

    def test_deletion_valid_obj_deletions_not_set(self):
        """
        Tests deletion of a valid object when deletions are not set.
        """
        smart_manager = G(
            SmartManager,
            manages_deletions=False,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertSmartManager',
            template={
                'char_field': 'hi',
                'int_field': 1,
            },
        )
        # Simulate re-saving
        smart_manager.save()

        upsert_model = UpsertModel.objects.get()
        self.assertEquals(upsert_model.char_field, 'hi')
        self.assertEquals(upsert_model.int_field, 1)

        # Delete the model template object, resulting in the deleting of the object it manages
        smart_manager.delete()
        self.assertEquals(UpsertModel.objects.count(), 1)
