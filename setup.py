from setuptools import setup, find_packages
import os

try:
    long_description = open('README.rst').read()
except IOError:
    long_description = ''

try:
    reqs = open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''

setup(
    name='django-treepages',
    description='A way to handle hierarchical flatpages in django.',
    long_description=long_description,
    author='Martin Ogden',
    author_email='martin@cahoona.co.uk',
    include_package_data=True,
    url='http://github.com/martinogden/django-treepages',
    packages=find_packages(),
    classifiers=[
        'Framework :: Django',
    ],
    install_requires = reqs,
    dependency_links = []
)
