from model_template.base import BaseModelTemplate
from model_template.tests.models import UpsertModel


class UpsertModelTemplate(BaseModelTemplate):
    def build(self):
        self.build_obj(UpsertModel, char_field=self._template['char_field'], updates={
            'int_field': self._template['int_field'],
        })


class UpsertModelListTemplate(BaseModelTemplate):
    def build(self):
        for template in self._template:
            self.build_obj(UpsertModel, char_field=template['char_field'], updates={
                'int_field': template['int_field'],
            })
