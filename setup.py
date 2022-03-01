from setuptools import setup

setup(
    name='dircompare',
    version='0.1',
    py_modules=['dircompare'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        dirCompare=dircompare.cli:main
    ''',
)