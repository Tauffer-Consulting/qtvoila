#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['PySide6', 'voila', 'numpy', 'psutil']

setup_requirements = []

test_requirements = []

setup(
    author="Luiz Tauffer",
    author_email='luiz@taufferconsulting.com',
    python_requires='>=3.5',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A Qt for Python extension for Voila",
    install_requires=requirements,
    license="BSD license",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='qtvoila',
    name='qtvoila',
    packages=find_packages(include=['qtvoila', 'qtvoila.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/luiztauffer/qtvoila',
    version='2.0.0',
    zip_safe=False,
)
