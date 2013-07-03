# -*- coding:utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os

version = '1.0'

long_description = (open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
                    open(os.path.join("docs", "CREDITS.txt")).read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read())


description = u'APyB: Conference Management'

setup(name='apyb.conference',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries :: Python Modules"],
      keywords='pythonbrasil apyb conference',
      author='APyB: Associao Python Brasil',
      author_email='contato@python.org.br',
      url='http://www.plone.org.br/gov/',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['apyb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.z3cform.datagridfield',
          'plone.app.users',
          'plone.app.dexterity [grok, relations]',
      ],
      extras_require={
          'develop': [
              'Sphinx',
              'manuel',
              'pep8',
              'setuptools-flakes',
          ],
          'test': [
              'interlude',
              'plone.app.testing'
          ]},
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
