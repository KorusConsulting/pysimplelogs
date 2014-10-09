import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pysimplelogs',
    version='0.3.3',
    url='https://github.com/Se7ge/pysimplelogs',
    author='Dmitry Timofeev',
    description='Python client library for [Simplelogs] [sl] logging system.',
    long_description=read('readme.md'),
    include_package_data=True,
    packages=['pysimplelogs'],
    platforms='any',
    test_suite='pysimplelogs.tests',
    install_requires=[
        'Requests',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
