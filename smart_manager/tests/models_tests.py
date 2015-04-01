from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django_dynamic_fixture import G, N

from smart_manager.models import SmartManager, SmartManagerObject
from smart_manager.tests.models import UpsertModel, RelModel, CantCascadeModel
from smart_manager.tests.smart_managers import UpsertModelListTemplate


class SmartManagerMixinTest(TransactionTestCase):
    """
    Tests the SmartManagerMixin class.
    """
    def test_smart_create(self):
        """
        Tests smart_create.
        """
        sm = UpsertModel.objects.smart_create(
            UpsertModelListTemplate, [{
                'char_field': 'valid',
                'int_field': 1,
            }])
        self.assertIsNone(sm.name)
        self.assertIsNotNone(sm.id)
        self.assertEquals(sm.smart_manager_class, 'smart_manager.tests.smart_managers.UpsertModelListTemplate')
        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertTrue(UpsertModel.objects.filter(char_field='valid', int_field=1).exists())

    def test_smart_dup_create(self):
        """
        Tests smart_create with integrity errors.
        """
        UpsertModel.objects.smart_create(
            UpsertModelListTemplate, [{
                'char_field': 'valid',
                'int_field': 1,
            }])
        with self.assertRaises(IntegrityError):
            UpsertModel.objects.smart_create(
                UpsertModelListTemplate, [{
                    'char_field': 'valid',
                    'int_field': 1,
                }])


class SmartModelMixinTest(TestCase):
    """
    Tests functionality in the SmartModelMixin.
    """
    def test_smart_upsert_non_persisted(self):
        """
        Tests a smart upsert on a non persisted model.
        """
        with self.assertRaises(ValueError):
            UpsertModel().smart_upsert(UpsertModelListTemplate, [{
                'char_field': 'valid',
                'int_field': 1,
            }])

    def test_smart_upsert(self):
        """
        Tests a smart upsert
        """
        um = G(UpsertModel, char_field='valid', int_field=1)

        um.smart_upsert(UpsertModelListTemplate, [{
            'char_field': 'valid',
            'int_field': 1,
        }])
        self.assertEquals(SmartManager.objects.count(), 1)
        self.assertEquals(SmartManagerObject.objects.count(), 1)

        um.smart_upsert(UpsertModelListTemplate, [{
            'char_field': 'valid2',
            'int_field': 2,
        }])
        self.assertEquals(SmartManager.objects.count(), 1)
        self.assertEquals(SmartManagerObject.objects.count(), 1)

        um = UpsertModel.objects.get()
        self.assertEquals(um.char_field, 'valid2')
        self.assertEquals(um.int_field, 2)

    def test_smart_delete_no_smart_manager(self):
        """
        Tests smart_delete when there was no previous smart manager.
        """
        um = G(UpsertModel, char_field='valid', int_field=1)
        um.smart_delete()

        self.assertFalse(UpsertModel.objects.filter(id=um.id).exists())

    def test_smart_delete_w_smart_manager(self):
        """
        Tests smart_delete when a smart manager exists.
        """
        UpsertModel.objects.smart_create(UpsertModelListTemplate, [{
            'char_field': 'valid',
            'int_field': 1,
        }])
        um = UpsertModel.objects.get()
        um.smart_delete()

        self.assertFalse(UpsertModel.objects.exists())
        self.assertFalse(SmartManager.objects.exists())


class ValidationTest(TransactionTestCase):
    """
    Tests that validation works appropriately.
    """
    def test_multi_null(self):
        """
        Tests that multiple smart managers with a null name can be created.
        """
        SmartManager.objects.create(
            name=None, smart_manager_class='smart_manager.tests.smart_managers.UpsertModelListTemplate',
            template=[{
                'char_field': 'valid1',
                'int_field': 1
            }],
        )
        SmartManager.objects.create(
            name=None, smart_manager_class='smart_manager.tests.smart_managers.UpsertModelListTemplate',
            template=[{
                'char_field': 'valid2',
                'int_field': 1
            }],
        )

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
    def test_str(self):
        smart_manager = SmartManager(name='hi')
        self.assertEquals(str(smart_manager), 'hi')

    def test_undeletable_object(self):
        """
        Tests deleting elements from the template of a smart manager when the elements are not
        deletable.
        """
        smart_manager = G(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.DontDeleteUpsertSmartManager',
            template={
                'char_field': 'hi',
                'int_field': 1,
            },
        )

        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())

        # All objects should still exist even after deleting them from the template and deleting the
        # smart manager itself
        smart_manager.template = {
            'char_field': 'hello',
            'int_field': 2,
        }
        smart_manager.save()

        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

        smart_manager.delete()
        self.assertEquals(UpsertModel.objects.count(), 2)

    def test_primary_obj_set(self):
        """
        Tests that the primary object is set during saving.
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

        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertEquals(smart_manager.primary_obj_id, UpsertModel.objects.get().id)
        self.assertEquals(smart_manager.primary_obj_type, ContentType.objects.get_for_model(UpsertModel))

        # Refresh the smart manager and verify the primary object params were persisted
        smart_manager = SmartManager.objects.get(id=smart_manager.id)
        self.assertEquals(smart_manager.primary_obj_id, UpsertModel.objects.get().id)
        self.assertEquals(smart_manager.primary_obj_type, ContentType.objects.get_for_model(UpsertModel))

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

    def test_deletion_protected_model(self):
        """
        Tests when a cascade delete cant occur becasue of a protected model.
        """
        rel_model = G(RelModel)
        G(CantCascadeModel, rel_model=rel_model)

        smart_manager = G(
            SmartManager,
            manages_deletions=True,
            smart_manager_class='smart_manager.tests.smart_managers.UpsertSmartManager',
            template={
                'char_field': 'hi',
                'int_field': 1,
            },
        )
        SmartManagerObject.objects.create(smart_manager=smart_manager, model_obj=rel_model)

        smart_manager.delete()

        # The rel model should still exist since its protected. The smart manager object
        # should not
        self.assertFalse(SmartManagerObject.objects.exists())
        self.assertTrue(RelModel.objects.exists())

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
