from setuptools import setup, find_packages

setup(
    name='tally',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'sqlalchemy',
        'pandas',
    ],
    entry_points='''
        [console_scripts]
        tally=tally.cli:cli
    ''',
)
