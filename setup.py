import os

from setuptools import setup, find_packages

import systemjs


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


readme = read_file('README.rst')
requirements = [
    'django-appconf>=0.6',
    'semantic_version',
]
test_requirements = [
    'mock',
    'coverage',
]

setup(
    name='django-systemjs',
    version=systemjs.__version__,
    license='MIT',

    # Packaging
    packages=find_packages(exclude=('tests', 'tests.*', 'examples')),
    install_requires=requirements,
    include_package_data=True,
    extras_require={
        'test': test_requirements,
    },
    scripts=['bin/trace-deps.js'],
    tests_require=test_requirements,
    test_suite='runtests.runtests',

    # PyPI metadata
    description='Brings SystemJS to Django staticfiles',
    long_description=readme,
    author='Sergei Maertens',
    author_email='sergeimaertens@gmail.com',
    platforms=['any'],
    url='https://github.com/sergei-maertens/django-systemjs',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ]
)
