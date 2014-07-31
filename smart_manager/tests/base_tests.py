from django.test import TestCase
from mock import patch

from smart_manager.base import BaseSmartManager
from smart_manager.tests.smart_managers import UpsertSmartManager
from smart_manager.tests.models import UpsertModel


class BaseSmartManagerTest(TestCase):
    """
    Tests functionality in the base model template.
    """
    def test_template_deepcopy(self):
        """
        Tests that the template can be modified after and it is still intact in the template
        class.
        """
        template = {'hello': 'world'}
        smart_manager = BaseSmartManager(template)

        # Modify the input template
        template['hello'] = 'world2'

        # The template in the model template should remain the same
        self.assertEquals(smart_manager._template, {'hello': 'world'})

    def test_build_object(self):
        """
        Tests that the build_object function upserts the object and adds it to the built objects list.
        """
        smart_manager = BaseSmartManager({})
        smart_manager.build_obj(UpsertModel, char_field='hi', updates={
            'int_field': 1,
        })
        smart_manager.build_obj(UpsertModel, char_field='hi', updates={
            'int_field': 2,
        })

        # There should be one UpsertModel with an int_field of 2
        upsert_model = UpsertModel.objects.get()
        self.assertEquals(upsert_model.char_field, 'hi')
        self.assertEquals(upsert_model.int_field, 2)
        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertEquals(smart_manager.built_objs, set([upsert_model]))

    def test_build_using(self):
        """
        Tests building using another model template.
        """
        smart_manager = BaseSmartManager({})
        built_objs = smart_manager.build_using(UpsertSmartManager, {'int_field': 1, 'char_field': '2'})
        self.assertTrue(type(built_objs) in (list, tuple,))

        upsert_model = UpsertModel.objects.get()
        self.assertEquals(upsert_model.int_field, 1)
        self.assertEquals(upsert_model.char_field, '2')
        self.assertEquals(UpsertModel.objects.count(), 1)
        self.assertEquals(smart_manager.built_objs, set([upsert_model]))

    @patch('smart_manager.tests.smart_managers.UpsertSmartManager.build', spec_set=True)
    def test_multi_build_using(self, mock_build):
        """
        Hits the branch for .build returning a list or tuple
        :type mock_build: Mock
        """
        mock_build.return_value = ['one', 'two']

        smart_manager = BaseSmartManager({})
        built_objs = smart_manager.build_using(UpsertSmartManager, {'int_field': 1, 'char_field': '2'})
        self.assertTrue(type(built_objs) in (list, tuple,))
