#!/usr/bin/env python3

import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='slt',
    description='Labeling tools for satellite imagery',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jindrich Stastka, Jakub Seidl, Blanka Gvozdikova',
    author_email='jindrich.stastka@chmi.cz, jakub.seidl@email.cz, blanka.gvozdikova@chmi.cz',
    classifiers=['Programming Language :: Python :: 3.7'],
    packages=['slt'],
    install_requires=[
        'dash==2.0.0',
        'dash-bootstrap-components==0.13.0',
        'gunicorn==20.1.0',
        'numpy>=1.19',
        'pandas==1.1.2',
        'plotly==5.3.1',
        'scikit-image==0.18.3',
        'scipy==1.7.1',
        'satellite-dataloader @ git+https://github.com/CHMI-satellite-department/satellite-dataloader@develop#egg=satellite-dataloader'
    ],
    scripts=['bin/slt'],
    include_package_data=True,
    zip_safe=False
)
