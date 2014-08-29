from smart_manager import BaseSmartManager
from smart_manager.tests.models import UpsertModel


class UpsertSmartManager(BaseSmartManager):
    def build(self):
        return self.build_obj(UpsertModel, char_field=self._template['char_field'], updates={
            'int_field': self._template['int_field'],
        })


class UpsertModelListTemplate(BaseSmartManager):
    def build(self):
        for template in self._template:
            self.build_obj(UpsertModel, char_field=template['char_field'], updates={
                'int_field': template['int_field'],
            })


class DontDeleteUpsertSmartManager(BaseSmartManager):
    def build(self):
        return self.build_obj(UpsertModel, char_field=self._template['char_field'], updates={
            'int_field': self._template['int_field'],
        }, is_deletable=False)
