from django.test import TestCase
from django_dynamic_fixture import G

from model_template.models import ModelTemplate
from model_template.tests.models import UpsertModel


class ModelTemplateTest(TestCase):
    """
    Tests custom functionality in the ModelTemplate class.
    """
    def test_template_changes(self):
        """
        Tests chaning the template and resaving.
        """
        model_template = G(
            ModelTemplate,
            manages_deletions=True,
            model_template_class='model_template.tests.model_templates.UpsertModelListTemplate',
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

        model_template.template = [{
            'char_field': 'hi',
            'int_field': 1,
        }]
        model_template.save()

        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())

        model_template.delete()
        self.assertFalse(UpsertModel.objects.exists())

    def test_template_changes_no_deletions(self):
        """
        Tests chaning the template and resaving when the template model does not manage deletions.
        """
        model_template = G(
            ModelTemplate,
            manages_deletions=False,
            model_template_class='model_template.tests.model_templates.UpsertModelListTemplate',
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

        model_template.template = [{
            'char_field': 'hi',
            'int_field': 1,
        }]
        model_template.save()

        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

        model_template.delete()
        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

    def test_build_multiple_distinct_objs_delete(self):
        model_template = G(
            ModelTemplate,
            manages_deletions=True,
            model_template_class='model_template.tests.model_templates.UpsertModelListTemplate',
            template=[{
                'char_field': 'hi',
                'int_field': 1,
            }, {
                'char_field': 'hello',
                'int_field': 2,
            }],
        )
        # Simulate re-saving
        model_template.save()

        self.assertEquals(UpsertModel.objects.count(), 2)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())
        self.assertTrue(UpsertModel.objects.filter(char_field='hello', int_field=2).exists())

        model_template.delete()
        self.assertFalse(UpsertModel.objects.exists())

    def test_build_multiple_same_objs(self):
        model_template = G(
            ModelTemplate,
            manages_deletions=True,
            model_template_class='model_template.tests.model_templates.UpsertModelListTemplate',
            template=[{
                'char_field': 'hi',
                'int_field': 1,
            }, {
                'char_field': 'hi',
                'int_field': 1,
            }],
        )
        # Simulate re-saving
        model_template.save()

        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertTrue(UpsertModel.objects.filter(char_field='hi', int_field=1).exists())

        model_template.delete()
        self.assertFalse(UpsertModel.objects.exists())

    def test_deletion_valid_obj_deletions_set(self):
        """
        Tests deletion of a valid object when deletions are set.
        """
        model_template = G(
            ModelTemplate,
            manages_deletions=True,
            model_template_class='model_template.tests.model_templates.UpsertModelTemplate',
            template={
                'char_field': 'hi',
                'int_field': 1,
            },
        )
        # Simulate re-saving
        model_template.save()

        upsert_model = UpsertModel.objects.get()
        self.assertEquals(upsert_model.char_field, 'hi')
        self.assertEquals(upsert_model.int_field, 1)

        # Delete the model template object, resulting in the deleting of the object it manages
        model_template.delete()
        self.assertEquals(UpsertModel.objects.count(), 0)

    def test_deletion_valid_obj_deletions_not_set(self):
        """
        Tests deletion of a valid object when deletions are not set.
        """
        model_template = G(
            ModelTemplate,
            manages_deletions=False,
            model_template_class='model_template.tests.model_templates.UpsertModelTemplate',
            template={
                'char_field': 'hi',
                'int_field': 1,
            },
        )
        # Simulate re-saving
        model_template.save()

        upsert_model = UpsertModel.objects.get()
        self.assertEquals(upsert_model.char_field, 'hi')
        self.assertEquals(upsert_model.int_field, 1)

        # Delete the model template object, resulting in the deleting of the object it manages
        model_template.delete()
        self.assertEquals(UpsertModel.objects.count(), 1)
