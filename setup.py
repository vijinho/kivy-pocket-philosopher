try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    version='1.0',
    name='aforgizmo',
    description='Aforgizmo Aphorisms',
    author='Vijay Mahrra',
    url='https://github.com/vijinho/aforgizmo',
    download_url='https://github.com/vijinho/aforgizmo',
    py_modules=['aforgizmo'],
    install_requires=[
        'Click',
        'Peewee',
        'nose'
    ],
    packages=['aforgizmo'],
    scripts=[],
    entry_points='''
        [console_scripts]
        aforgizmo=aforgizmo:cli
    '''
)
