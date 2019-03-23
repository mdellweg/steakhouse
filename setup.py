from setuptools import setup, find_packages

setup(
    name='steakhouse',
    version="0.1b",
    description='An sql-database backed job queue',
    author='Matthias Dellweg',
    author_email='dellweg@atix.de',
    licence='GPLv3',
    packages=find_packages(),
    install_requires=[
        'click',
        'peewee',
    ],
    entry_points='''
        [console_scripts]
        sh_manager=steakhouse.manager:cli
    ''',
)
