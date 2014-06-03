from django.test import TestCase

from model_template import admin


class AdminTest(TestCase):
    def test_admin(self):
        """
        Verify the admin is registered properly.
        """
        assert(admin)
