from django.test import TestCase

from model_template.base import BaseModelTemplate
from model_template.tests.models import UpsertModel


class UpsertModelTemplate(BaseModelTemplate):
    def build(self):
        self.build_obj(UpsertModel, char_field=self._template['char_field'], updates={
            'int_field': self._template['int_field'],
        })


class BaseModelTemplateTest(TestCase):
    """
    Tests functionality in the base model template.
    """
    def test_template_deepcopy(self):
        """
        Tests that the template can be modified after and it is still intact in the template
        class.
        """
        template = {'hello': 'world'}
        model_template = BaseModelTemplate(template)

        # Modify the input template
        template['hello'] = 'world2'

        # The template in the model template should remain the same
        self.assertEquals(model_template._template, {'hello': 'world'})

    def test_build_object(self):
        """
        Tests that the build_object function upserts the object and adds it to the built objects list.
        """
        model_template = BaseModelTemplate({})
        model_template.build_obj(UpsertModel, char_field='hi', updates={
            'int_field': 1,
        })
        model_template.build_obj(UpsertModel, char_field='hi', updates={
            'int_field': 2,
        })

        # There should be one UpsertModel with an int_field of 2
        upsert_model = UpsertModel.objects.get()
        self.assertEquals(upsert_model.char_field, 'hi')
        self.assertEquals(upsert_model.int_field, 2)
        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertEquals(model_template.built_objs, set([upsert_model]))

    def test_build_using(self):
        """
        Tests building using another model template.
        """
        model_template = BaseModelTemplate({})
        model_template.build_obj_using(UpsertModelTemplate, {'int_field': 1, 'char_field': '2'})

        upsert_model = UpsertModel.objects.get()
        self.assertEquals(upsert_model.int_field, 1)
        self.assertEquals(upsert_model.char_field, '2')
        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertEquals(model_template.built_objs, set([upsert_model]))
