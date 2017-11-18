# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='glc',
      version='0.1.0',
      description='glc implementation',
      license='GPL-2',
      author='Paul Healy',
      url='https://github.com/lmiphay/glc',
      packages=[
          'bun'
      ],
      install_requires=['invoke', 'pyyaml'],
      entry_points={
        'console_scripts': ['glc = glc.main:program.run']
      },
      data_files=[
            ('/etc/glc', [
                  'etc/glc.yaml'
            ]),
            ('share/oam/site', [
                  'share/oam/site/glc.py'
            ])
      ]
)
