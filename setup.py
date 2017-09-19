# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'smart_manager/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-smart-manager',
    version=get_version(),
    description='Make templates that manage models',
    long_description=open('README.md').read(),
    url='https://github.com/ambitioninc/django-smart-manager',
    author='Wes Kendall',
    author_email='opensource@ambition.com',
    keywords='Django, Models, ORM, Manager, Templates',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
    ],
    license='MIT',
    install_requires=[
        'Django>=1.9',
        'django-manager-utils>=0.13.0',
        'jsonfield>=0.9.20',
    ],
    tests_require=[
        'psycopg2',
        'django-dynamic-fixture',
        'django-nose>=1.4',
        'mock',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)
