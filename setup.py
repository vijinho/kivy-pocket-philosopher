import os

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    version='1.0',
    name='aforgizmo',
    description='Pocket Philosopher',
    long_description='Pocket Philosopher (Aforgizmo Aphorisms) is a tool to store and display aphorisms.',
    platforms = ['Linux','OSX','Android'],
    author='Vijay Mahrra',
    license='GPL3.0',
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Desktop Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License V3.0',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: Google :: Android',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications :: Personal'
          ],
    url='https://github.com/vijinho/aforgizmo',
    download_url='https://github.com/vijinho/aforgizmo',
    package_dir = {'': 'aforgizmo'},
    data_files=[
        ('data', ['data/aphorisms.db', 'data/aphorisms.json']),
        ('assets', [
            'assets/fonts/roboto/Apache License.txt',
            'assets/fonts/roboto/RobotoSlab-Bold.ttf',
            'assets/fonts/roboto/RobotoSlab-Light.ttf',
            'assets/fonts/roboto/RobotoSlab-Regular.ttf',
            'assets/fonts/roboto/RobotoSlab-Thin.ttf',
            'assets/img/bg/COPYRIGHT.rst',
            'assets/img/bg/IMGP1149_1.jpg',
            'assets/img/bg/IMGP1155_1.jpg',
            'assets/img/bg/IMGP1181_2.jpg',
            'assets/img/bg/IMGP1221_1.jpg',
            'assets/img/bg/IMGP1308_1.jpg',
            'assets/img/bg/IMGP1313_1.jpg',
            'assets/img/bg/IMGP1324_2.jpg',
            'assets/img/icon.png',
            'assets/img/icons/about.png',
            'assets/img/icons/edit.png',
            'assets/img/icons/help.png',
            'assets/img/icons/list.png',
            'assets/img/icons/new.png',
            'assets/img/icons/quit.png',
            'assets/img/icons/search.png',
            'assets/img/icons/settings.png',
            'assets/img/icons/warning.png',
            'assets/img/logo.png']
        ),
    ],
    py_modules=['aforgizmo'],
    install_requires=[
        'nose>=1.3.4',
        'Click>=3.3',
        'Peewee>=2.3.3',
        #'kivy>=1.8.0'
    ],
    packages=[],
    scripts=[],
    entry_points='''
        [console_scripts]
        aforgizmo=cli:cli
        #[gui_scripts]
        #aforgizmo_gui=main:run
    '''
)
