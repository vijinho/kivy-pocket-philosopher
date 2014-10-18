from setuptools import setup

setup(
    name='Aforgizmo',
    version='1.0',
    py_modules=['aforgizmo'],
    install_requires=[
        'Click',
        'Peewee'
    ],
    entry_points='''
        [console_scripts]
        aforgizmo=aforgizmo:cli
    '''
)
