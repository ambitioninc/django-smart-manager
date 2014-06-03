[![Build Status](https://travis-ci.org/ambitioninc/django-entity.png)](https://travis-ci.org/ambitioninc/django-model-template)
Django Model Template
==================
Django Model Template provides a simple framework for representing and managing Django models from serializable templates.


#Problem Overview

Oftentimes what we model in Django spans multiple objects and tables. Managing a single object that is represented by multiple models can be quite cumbersome through the shell or through basic Django administration. This app provides a framework such that a user can write templates that represent many models and complex relationships.

For example, assume that you model a person. The ``Person`` model contains a unique identifier for that person, multiple ``PhoneNumber`` models that point to it, and multiple ``Address`` models. With Django Model Template, one can construct a template in the following manner:

```python
{
    'unique_id': 'person_unique_id':
    'phone_numbers': ['865-123-4985', '956-345-5678'],
    'addresses': [{
        'street': 'my street address1',
        'city': 'my city',
    }],
}
```

Using the framework (as shown soon), we can construct a parser for this template that maintains the appropriate model representation underneath while also providing a much simpler way to manage all of those underlying models. This management includes updates to the data in the template and deletions to objects in the template.

# Building the Person Example
Before we show how to build the example just illustrated in the problem overview, the models in the example are laid out below:

```python
class Person(models.Model):
    unique_id = models.CharField(max_length=64, unique=True)


class PhoneNumber(models.Model):
    person = models.ForeignKey(Person)
    number = models.CharField(max_length=32)


class Address(models.Model):
    person = models.ForeignKey(Person)
    street = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
```

In order to achieve the ability of specifying the ``Person`` model (and its related models) via a template as shown above, the user must create a model template class that inherits ``BaseModelTemplate``. This class will be responsible for taking in the template and managing the object(s) represented by the template.

For the sake of example, let's assume we're going to build three model template classes: one to manage addresses, one to manage phone numbers, and one to manage a person and its associated addresses and phone numbers. We'll begin from the bottom up by building the ``Address`` model template. The code for this is shown below:

```
from model_template import BaseModelTemplate


class AddressModelTemplate(BaseModelTemplate):
    def build(self):
        self.build_obj(person_id=self._template['person'], street=self._template['street'], city=self._template['city'])
```

Now that we have this class, it can be called in the following way to build its associated object:

```python
AddressModelTemplate({
    'person': 1,  # The pk of a Person object
    'street': 'my street',
    'city': 'my city',
}).build()
```

Underneath the hood, it is passing the parameters of build_obj to the ``upsert`` function [Django Manager Utils](https://github.com/ambitioninc/django-manager-utils) and also internally maintaining all of the objects that have been built.

Now that the model template class has been created, a ``ModelTemplate`` model can be constructed as follows:

```python
from model_template import ModelTemplate


mt = ModelTemplate.objects.create(model_template_class='path.to.AddressModelTemplate', template={
    'person': 1,
    'street': 'my street',
    'city': 'my city',
})
```

Once this model is created, it manages all of the objects associated with the template. If the user was to change the template and save the ``mt`` variable from the example, the underlying ``Address`` model would be updated. Similarly, the underlying ``Address`` model will also be deleted when ``mt`` is deleted. The deletion behavior can be turned off by specifying ``manages_deletions=False`` in the creation of the model template.

While this example is trivial, the power of Django Model Template is unleashed when you start to build more and more complex objects that need ot be managed. Let's assume that the user can now build the associated ``PhoneNumberModelTemplate`` class for creating ``PhoneNumber`` objects and move on to creating the ``PersonModelTemplate`` model template class:

```python
class PersonModelTemplate(BaseModelTemplate):
    def build(self):
        # Build the parent person object
        person = self.build_obj(unique_id=self._template['unique_id'])

        # Build its child phone number objects using the PhoneNumberModelTemplate
        for phone_number in self._template['phone_numbers']:
            self.build_obj_using(PhoneModelTemplate, {
                'person': person.id,
                'phone_number': phone_number
            })

        # Build its child address objects using the AddressModelTemplate
        for address in self._template['addresses']:
            self.build_obj_using(AddressModelTemplate, {
                'person': person.id,
                'street': address['street'],
                'city': address['city'],
            })
```

Note that the ``PersonModelTemplate`` uses the ``build_obj_using`` function to build an object using another model template. This ensures that the objects managed by that model template are also managed by the calling model template.

Similarly, one can now make a ``ModelTemplate`` object using this model template class to manage a complete ``Person`` object.
