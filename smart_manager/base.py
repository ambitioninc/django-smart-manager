from copy import deepcopy

from manager_utils import upsert


class BaseSmartManager(object):
    def __init__(self, template):
        self._template = deepcopy(template)
        self._built_objs = set()

    @property
    def built_objs(self):
        return self._built_objs

    def build_obj(self, model_class, is_deletable=True, updates=None, defaults=None, **kwargs):
        """
        Builds an object using the upsert function in manager utils. If the object can be deleted
        by the smart manager, it is added to the internal _built_objs list and returned.
        """
        built_obj = upsert(model_class.objects, updates=updates, defaults=defaults, **kwargs)[0]
        if is_deletable:
            self._built_objs |= set([built_obj])

        return built_obj

    def build_using(self, smart_manager_class, template):
        """
        Builds objects using another builder and a template. Adds the resulting built objects
        from that builder to the built objects of this builder.
        """
        smart_manager = smart_manager_class(template)
        built_objs = smart_manager.build()
        self._built_objs |= smart_manager.built_objs

        # make sure build objs is a list or tuple
        if type(built_objs) not in (list, tuple,):
            built_objs = [built_objs]

        return built_objs

    def build(self):
        """
        All builders must implement the build function, which returns the built object. All build
        functions must also maintain an interal list of built objects, which are accessed by
        self.built_objs.
        """
        raise NotImplementedError
